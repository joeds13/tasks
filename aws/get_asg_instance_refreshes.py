#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
from datetime import datetime, timedelta, timezone

import boto3

session = boto3.Session()
asg_client = session.client("autoscaling")
cloudwatch_client = session.client("cloudwatch")
elb_client = session.client("elbv2")

# Get the account name
sts_client = session.client("sts")
account_id = sts_client.get_caller_identity()["Account"]
print(f"Processing account ID: {account_id}")

# Get all ASGs
paginator = asg_client.get_paginator("describe_auto_scaling_groups")
asg_pages = paginator.paginate()

# Get all load balancers
lb_paginator = elb_client.get_paginator("describe_load_balancers")
lb_pages = lb_paginator.paginate()
load_balancers = []
for page in lb_pages:
    for lb in page["LoadBalancers"]:
        if lb["Type"] == "application":
            load_balancers.append(lb)


for page in asg_pages:
    for asg in page["AutoScalingGroups"]:
        asg_name = ""
        asg_tags = asg.get("Tags", [])

        # Get ASG name from tags
        for tag in asg_tags:
            if tag["Key"] == "Name":
                asg_name = tag["Value"]
                break

        if not asg_name:
            asg_name = asg["AutoScalingGroupName"]

        # print(f"\nProcessing ASG: {asg_name}")

        # Get instance refreshes for each ASG
        try:
            refreshes = asg_client.describe_instance_refreshes(
                AutoScalingGroupName=asg["AutoScalingGroupName"]
            )["InstanceRefreshes"]
            # print(f"Found {len(refreshes)} instance refreshes")

            # Find matching load balancer by name prefix
            matching_lbs = []
            asg_prefix = asg_name[:6]
            for lb in load_balancers:
                lb_name = lb["DNSName"]
                # print(f"Checking load balancer: {lb_name} for: {asg_prefix}")
                if asg_prefix in lb_name:
                    matching_lbs.append(lb)

            # print(f"Found {len(matching_lbs)} matching load balancers")

            for refresh in refreshes:
                # print(f"\nProcessing refresh: {refresh.get('InstanceRefreshId')}")
                start_time = refresh["StartTime"]
                end_time = refresh.get("EndTime", "Still in progress")

                if end_time != "Still in progress":
                    start_time = start_time.astimezone(timezone.utc)
                    end_time = end_time.astimezone(timezone.utc)
                    # print(f"Time window: {start_time} to {end_time}")

                    # Calculate day start and end times
                    day_start = datetime(
                        start_time.year,
                        start_time.month,
                        start_time.day,
                        tzinfo=timezone.utc,
                    )
                    day_end = day_start + timedelta(days=1)

                    # Process each matching load balancer
                    for lb in matching_lbs:
                        lb_arn = lb["LoadBalancerArn"]
                        lb_name = (
                            f"app/{lb_arn.split('/')[-2] + '/' + lb_arn.split('/')[-1]}"
                        )
                        # print(f"\nProcessing load balancer: {lb_name}")

                        # print("Fetching request count metrics...")
                        # Get metrics during the refresh window
                        total_requests = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/ApplicationELB",
                            MetricName="RequestCount",
                            Dimensions=[
                                {
                                    "Name": "LoadBalancer",
                                    "Value": lb_name,
                                }
                            ],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=300,
                            Statistics=["Sum"],
                        )
                        # print(total_requests)

                        # print("Fetching 5XX error metrics...")
                        target_5xx = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/ApplicationELB",
                            MetricName="HTTPCode_ELB_5XX_Count",
                            Dimensions=[
                                {
                                    "Name": "LoadBalancer",
                                    "Value": lb_name,
                                }
                            ],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=300,
                            Statistics=["Sum"],
                        )

                        # Get daily metrics
                        daily_requests = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/ApplicationELB",
                            MetricName="RequestCount",
                            Dimensions=[
                                {
                                    "Name": "LoadBalancer",
                                    "Value": lb_name,
                                }
                            ],
                            StartTime=day_start,
                            EndTime=day_end,
                            Period=300,
                            Statistics=["Sum"],
                        )

                        daily_5xx = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/ApplicationELB",
                            MetricName="HTTPCode_ELB_5XX_Count",
                            Dimensions=[
                                {
                                    "Name": "LoadBalancer",
                                    "Value": lb_name,
                                }
                            ],
                            StartTime=day_start,
                            EndTime=day_end,
                            Period=300,
                            Statistics=["Sum"],
                        )

                        total_req_sum = 0
                        if total_requests["Datapoints"]:
                            total_req_sum = sum(
                                [dp["Sum"] for dp in total_requests["Datapoints"]]
                            )

                        total_5xx_sum = 0
                        if target_5xx["Datapoints"]:
                            total_5xx_sum = sum(
                                [dp["Sum"] for dp in target_5xx["Datapoints"]]
                            )

                        daily_req_sum = 0
                        if daily_requests["Datapoints"]:
                            daily_req_sum = sum(
                                [dp["Sum"] for dp in daily_requests["Datapoints"]]
                            )

                        daily_5xx_sum = 0
                        if daily_5xx["Datapoints"]:
                            daily_5xx_sum = sum(
                                [dp["Sum"] for dp in daily_5xx["Datapoints"]]
                            )

                        print(f"ASG: {asg_name}")
                        print(f"Load Balancer: {lb_arn}")
                        print(f"Refresh Start Time: {start_time}")
                        print(f"Refresh End Time: {end_time}")
                        print(f"Total Requests: {total_req_sum}")
                        print(f"Total 5XX Errors: {total_5xx_sum}")
                        error_percentage = (
                            (total_5xx_sum / total_req_sum * 100)
                            if total_req_sum > 0
                            else 0
                        )
                        print(f"5XX Error Percentage: {error_percentage:.2f}%")
                        print(f"Daily Total Requests: {daily_req_sum}")
                        daily_error_percentage = (
                            (100 - (total_5xx_sum / daily_req_sum * 100))
                            if daily_req_sum > 0
                            else 100
                        )
                        print(f"Availability SLI: {daily_error_percentage:.2f}%")
                        print("---")

        except asg_client.exceptions.ClientError as e:
            print(f"Error getting refreshes for ASG {asg_name}: {e}")
