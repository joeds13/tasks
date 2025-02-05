#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import boto3
import botocore


def ensure_vpc_peering_routes(routes):
    ec2 = boto3.client("ec2")

    for route in routes:
        try:
            # Check if route exists
            response = ec2.describe_route_tables(
                RouteTableIds=[route["route_table_id"]]
            )

            if "RouteTables" in response and len(response["RouteTables"]) > 0:
                for rt_route in response["RouteTables"][0]["Routes"]:
                    if (
                        rt_route.get("DestinationCidrBlock")
                        == route["destination_cidr_block"]
                        and rt_route.get("VpcPeeringConnectionId")
                        == route["peering_connection_id"]
                    ):
                        print(
                            f"Route exists in {route['route_table_id']} for CIDR {route['destination_cidr_block']} with peering connection {route['peering_connection_id']}"
                        )
                        break

        except botocore.exceptions.ClientError as e:
            print(f"Error processing route table {route['route_table_id']}: {str(e)}")
            continue


routes = [
    {
        "destination_cidr_block": "10.2.85.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0aee4c05297b7eb14",
    },
    {
        "destination_cidr_block": "10.2.85.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0c47f30b640e09203",
    },
    {
        "destination_cidr_block": "10.2.85.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0e3e65974f565292d",
    },
    {
        "destination_cidr_block": "10.2.85.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-044754b498532620a",
    },
    {
        "destination_cidr_block": "10.2.85.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-062f35ab6d09dbee0",
    },
    {
        "destination_cidr_block": "10.2.85.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-0dea0f67566441c23",
    },
    {
        "destination_cidr_block": "10.2.86.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0aee4c05297b7eb14",
    },
    {
        "destination_cidr_block": "10.2.86.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0c47f30b640e09203",
    },
    {
        "destination_cidr_block": "10.2.86.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0e3e65974f565292d",
    },
    {
        "destination_cidr_block": "10.2.86.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-044754b498532620a",
    },
    {
        "destination_cidr_block": "10.2.86.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-062f35ab6d09dbee0",
    },
    {
        "destination_cidr_block": "10.2.86.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-0dea0f67566441c23",
    },
    {
        "destination_cidr_block": "10.2.87.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0aee4c05297b7eb14",
    },
    {
        "destination_cidr_block": "10.2.87.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0c47f30b640e09203",
    },
    {
        "destination_cidr_block": "10.2.87.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0e3e65974f565292d",
    },
    {
        "destination_cidr_block": "10.2.87.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-044754b498532620a",
    },
    {
        "destination_cidr_block": "10.2.87.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-062f35ab6d09dbee0",
    },
    {
        "destination_cidr_block": "10.2.87.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-0dea0f67566441c23",
    },
    {
        "destination_cidr_block": "10.3.87.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-072ce4c7d686d0561",
    },
    {
        "destination_cidr_block": "10.3.86.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-072ce4c7d686d0561",
    },
    {
        "destination_cidr_block": "10.3.85.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-072ce4c7d686d0561",
    },
    {
        "destination_cidr_block": "10.0.85.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-072ce4c7d686d0561",
    },
    {
        "destination_cidr_block": "10.0.86.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-072ce4c7d686d0561",
    },
    {
        "destination_cidr_block": "10.0.87.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-072ce4c7d686d0561",
    },
    {
        "destination_cidr_block": "10.3.87.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-025dda25550e06b90",
    },
    {
        "destination_cidr_block": "10.3.86.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-025dda25550e06b90",
    },
    {
        "destination_cidr_block": "10.3.85.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-025dda25550e06b90",
    },
    {
        "destination_cidr_block": "10.0.85.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-025dda25550e06b90",
    },
    {
        "destination_cidr_block": "10.0.86.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-025dda25550e06b90",
    },
    {
        "destination_cidr_block": "10.0.87.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-025dda25550e06b90",
    },
    {
        "destination_cidr_block": "10.3.87.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0a0b250eaec216882",
    },
    {
        "destination_cidr_block": "10.3.86.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0a0b250eaec216882",
    },
    {
        "destination_cidr_block": "10.3.85.0/24",
        "peering_connection_id": "pcx-0a8d01852381a8e4b",
        "route_table_id": "rtb-0a0b250eaec216882",
    },
    {
        "destination_cidr_block": "10.0.85.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-0a0b250eaec216882",
    },
    {
        "destination_cidr_block": "10.0.86.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-0a0b250eaec216882",
    },
    {
        "destination_cidr_block": "10.0.87.0/24",
        "peering_connection_id": "pcx-001e0091370337bf6",
        "route_table_id": "rtb-0a0b250eaec216882",
    },
]

ensure_vpc_peering_routes(routes)
