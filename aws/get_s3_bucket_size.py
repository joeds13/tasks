#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import argparse

import boto3


def get_folder_size(bucket_name, folder_prefix):
    s3 = boto3.client("s3")
    total_size = 0

    # List all object versions in the bucket with the given prefix
    paginator = s3.get_paginator("list_object_versions")
    operation_parameters = {"Bucket": bucket_name, "Prefix": folder_prefix}

    # Iterate through all versions of all objects
    for page in paginator.paginate(**operation_parameters):
        # Add sizes of current versions
        if "Versions" in page:
            for version in page["Versions"]:
                total_size += version["Size"]

        # Add sizes of delete markers
        if "DeleteMarkers" in page:
            for marker in page["DeleteMarkers"]:
                total_size += 0  # Delete markers have no size

    return total_size


def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def list_subfolder_sizes(bucket_name, folder_prefix):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    operation_parameters = {
        "Bucket": bucket_name,
        "Prefix": folder_prefix,
        "Delimiter": "/",
    }

    result = paginator.paginate(**operation_parameters).build_full_result()

    # Calculate size of files in the current prefix level
    top_level_size = get_folder_size(bucket_name, folder_prefix)
    if top_level_size > 0:
        print(f"Size of files in {folder_prefix or '/'}: {format_size(top_level_size)}")

    # Calculate sizes for subfolders
    if "CommonPrefixes" in result:
        for prefix in result["CommonPrefixes"]:
            subfolder = prefix["Prefix"]
            size = get_folder_size(bucket_name, subfolder)
            print(f"Size of {subfolder}: {format_size(size)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="S3 bucket name")
    parser.add_argument("--prefix", help="Folder prefix", default="")
    args = parser.parse_args()

    if args.bucket:
        list_subfolder_sizes(args.bucket, args.prefix)
    else:
        s3 = boto3.client("s3")
        response = s3.list_buckets()

        for bucket in response["Buckets"]:
            bucket_name = bucket["Name"]
            print(f"\nAnalyzing bucket: {bucket_name}")
            list_subfolder_sizes(bucket_name, args.prefix)
