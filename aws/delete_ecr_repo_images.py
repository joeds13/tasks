#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import argparse
import os

import boto3

# AWS Configuration
REGION = "eu-west-1"  # Change to your region
REPO_NAME = os.getenv("REPO_NAME")  # Get repository name from environment variable

# Create ECR client
ecr_client = boto3.client("ecr", region_name=REGION)


def delete_all_images(repository_name, dry_run=True):
    try:
        # List all images with pagination
        image_ids = []
        paginator = ecr_client.get_paginator("list_images")
        for page in paginator.paginate(repositoryName=repository_name):
            image_ids.extend(page.get("imageIds", []))

        if not image_ids:
            print(f"No images found in repository {repository_name}.")
            return

        # Delete images in batches
        if dry_run:
            print(
                f"[DRY RUN] Would delete {len(image_ids)} images from repository {repository_name}"
            )
            for image in image_ids:
                print(f" - Would delete image: {image}")
            return

        print(f"Deleting {len(image_ids)} images from repository {repository_name}...")

        # Process images in batches of 100
        batch_size = 100
        for i in range(0, len(image_ids), batch_size):
            batch = image_ids[i : i + batch_size]
            response = ecr_client.batch_delete_image(
                repositoryName=repository_name, imageIds=batch
            )

            deleted_images = response.get("imageIds", [])
            failures = response.get("failures", [])

            if deleted_images:
                print(f"Successfully deleted batch of {len(deleted_images)} images.")
            if failures:
                print(f"Failed to delete {len(failures)} images in batch:")
                for failure in failures:
                    print(f" - {failure['imageId']} : {failure['failureReason']}")

    except Exception as e:
        print(f"Error deleting images: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute", action="store_true", help="Execute deletion (disable dry run)"
    )
    args = parser.parse_args()

    delete_all_images(REPO_NAME, dry_run=not args.execute)
