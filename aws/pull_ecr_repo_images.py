#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import os
import subprocess

import boto3

repo_name = os.getenv("REPO_NAME")
region = "eu-west-1"

account_id = os.environ["AWS_ACCOUNT_ID"]
ecr = boto3.client("ecr", region_name=region)
images = ecr.list_images(repositoryName=repo_name)["imageIds"]

for image in images:
    image_tag = image.get("imageTag")
    image_digest = image["imageDigest"]

    if image_tag:
        # Pull by tag if it exists
        subprocess.run(
            [
                "docker",
                "pull",
                f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}:{image_tag}",
            ]
        )
    else:
        # Pull by digest if tag is None
        subprocess.run(
            [
                "docker",
                "pull",
                f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}@{image_digest}",
            ]
        )
