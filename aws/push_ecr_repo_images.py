#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import os
import subprocess

# AWS and repository configuration
REGION = "eu-west-1"  # Change to your AWS region

REPO_NAME = os.environ.get("REPO_NAME")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID")

ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{REPO_NAME}"


def get_local_docker_images():
    cmd = (
        f'docker images --format "{{{{.Repository}}}}:{{{{.Tag}}}}" | grep "{ECR_URI}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def push_images_to_ecr():
    images = get_local_docker_images()

    if not images:
        print("No images found locally matching the ECR repository.")
        return

    # Authenticate with AWS ECR
    print("Authenticating with AWS ECR...")
    login_cmd = f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com"
    subprocess.run(login_cmd, shell=True, check=True)

    for image_tag in images.split("\n"):
        print(f"Pushing image: {image_tag} to ECR...")
        tag = image_tag.split(":")[1]
        push_cmd = f"docker push {ECR_URI}:{tag}"
        subprocess.run(push_cmd, shell=True, check=True)
        print(f"Successfully pushed: {image_tag}")

    print("All images have been pushed to ECR!")


push_images_to_ecr()
