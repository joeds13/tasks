#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import argparse
from datetime import datetime

import boto3


def delete_terratest_log_groups(dry_run=False):
    logs_client = boto3.client("logs")

    log_group_strings_to_delete = ["example"]

    try:
        paginator = logs_client.get_paginator("describe_log_groups")
        for page in paginator.paginate():
            for log_group in page["logGroups"]:
                log_group_name = log_group["logGroupName"]
                create_date = datetime.fromtimestamp(log_group["creationTime"] / 1000.0)

                # Get the latest log stream date
                latest_stream_date = None
                try:
                    stream_paginator = logs_client.get_paginator("describe_log_streams")
                    for stream_page in stream_paginator.paginate(
                        logGroupName=log_group_name,
                        orderBy="LastEventTime",
                        descending=True,
                    ):
                        if stream_page["logStreams"]:
                            latest_stream = stream_page["logStreams"][0]
                            if "lastEventTimestamp" in latest_stream:
                                latest_stream_date = datetime.fromtimestamp(
                                    latest_stream["lastEventTimestamp"] / 1000.0
                                )
                            break
                except Exception as e:
                    print(f"Error getting log streams for {log_group_name}: {str(e)}")

                if (
                    not any(
                        s.lower() in log_group_name.lower()
                        for s in log_group_strings_to_delete
                    )
                    and create_date.year == 2024
                ):
                    if dry_run:
                        message = f"Would delete log group: {log_group_name} (Created: {create_date}, Latest event: {latest_stream_date or 'No events'})"
                        if create_date.year == 2024 or (
                            latest_stream_date and latest_stream_date.year == 2024
                        ):
                            print(f"\033[33m{message}\033[0m")  # Orange text
                        else:
                            print(message)
                        continue

                    try:
                        print(f"Deleting log group: {log_group_name}")
                        logs_client.delete_log_group(logGroupName=log_group_name)
                        print(f"Successfully deleted log group: {log_group_name}")

                    except logs_client.exceptions.ResourceNotFoundException:
                        print(f"Log group {log_group_name} not found")
                    except Exception as e:
                        print(f"Error deleting log group {log_group_name}: {str(e)}")

    except Exception as e:
        print(f"Error listing log groups: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print log groups that would be deleted without actually deleting them",
    )
    args = parser.parse_args()
    delete_terratest_log_groups(dry_run=args.dry_run)
