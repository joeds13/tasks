import argparse
import json
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv(".env.sync_google_workspace_to_iam_idc")

# Google Workspace API settings
GOOGLE_WORKSPACE_API_SCOPE = os.getenv(
    "GOOGLE_WORKSPACE_API_SCOPE",
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
)
GOOGLE_WORKSPACE_API_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_WORKSPACE_API_CREDENTIALS_FILE", "credentials.json"
)

# AWS IAM Identity Center settings
AWS_IAM_IDENTITY_CENTER_REGION = os.getenv(
    "AWS_IAM_IDENTITY_CENTER_REGION", "eu-west-1"
)
AWS_IAM_IDENTITY_CENTER_CLIENT_ID = os.getenv(
    "AWS_IAM_IDENTITY_CENTER_CLIENT_ID", "your_client_id"
)
AWS_IAM_IDENTITY_CENTER_CLIENT_SECRET = os.getenv(
    "AWS_IAM_IDENTITY_CENTER_CLIENT_SECRET", "your_client_secret"
)
AWS_IAM_IDENTITY_CENTER_ACCESS_TOKEN_URL = (
    "https://cognito-idp.{}.amazonaws.com/token".format(AWS_IAM_IDENTITY_CENTER_REGION)
)

# AWS IAM Identity Center API settings
AWS_IAM_IDENTITY_CENTER_API_SCOPE = (
    "https://cognito-idp.{}.amazonaws.com/scope/profile".format(
        AWS_IAM_IDENTITY_CENTER_REGION
    )
)
AWS_IAM_IDENTITY_CENTER_API_CLIENT_ID = AWS_IAM_IDENTITY_CENTER_CLIENT_ID
AWS_IAM_IDENTITY_CENTER_API_CLIENT_SECRET = AWS_IAM_IDENTITY_CENTER_CLIENT_SECRET


def get_google_workspace_api_credentials():
    """Load Google Workspace API credentials from a file."""
    credentials = None
    if os.path.exists(GOOGLE_WORKSPACE_API_CREDENTIALS_FILE):
        with open(GOOGLE_WORKSPACE_API_CREDENTIALS_FILE, "r") as f:
            credentials = json.load(f)
    return credentials


def get_google_workspace_api_service():
    """Create a Google Workspace API service instance."""
    credentials = get_google_workspace_api_credentials()
    if not credentials:
        raise ValueError("Google Workspace API credentials file not found")
    service = build("admin", "directory_v1", credentials=credentials)
    return service


def get_aws_iam_identity_center_api_access_token():
    """Get an AWS IAM Identity Center API access token."""
    client_id = AWS_IAM_IDENTITY_CENTER_API_CLIENT_ID
    client_secret = AWS_IAM_IDENTITY_CENTER_API_CLIENT_SECRET
    access_token_url = AWS_IAM_IDENTITY_CENTER_ACCESS_TOKEN_URL
    import requests

    response = requests.post(
        access_token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise ValueError("Failed to get AWS IAM Identity Center API access token")
    return response.json()["access_token"]


def get_aws_iam_identity_center_api_service():
    """Create an AWS IAM Identity Center API service instance."""
    access_token = get_aws_iam_identity_center_api_access_token()
    service = boto3.client(
        "cognito-idp",
        region_name=AWS_IAM_IDENTITY_CENTER_REGION,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=access_token,
    )
    return service


def get_google_workspace_group_members(service, group_id):
    """Get the members of a Google Workspace group."""
    try:
        response = service.members().list(groupKey=group_id).execute()
        return response.get("members", [])
    except HttpError as e:
        raise ValueError("Failed to get Google Workspace group members: {}".format(e))


def create_aws_iam_identity_center_user(service, user_name, email):
    """Create a user in AWS IAM Identity Center."""
    try:
        response = service.sign_up(
            ClientId=AWS_IAM_IDENTITY_CENTER_API_CLIENT_ID,
            Username=user_name,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
        return response
    except ClientError as e:
        raise ValueError("Failed to create AWS IAM Identity Center user: {}".format(e))


def main():
    parser = argparse.ArgumentParser(
        description="Sync Google Workspace group members with AWS IAM Identity Center users"
    )
    parser.add_argument("--group-id", required=True, help="Google Workspace group ID")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--execute", action="store_true", help="Execute mode")
    args = parser.parse_args()

    if not args.execute and not args.dry_run:
        raise ValueError("Either --dry-run or --execute flag must be specified")

    service = get_google_workspace_api_service()
    group_members = get_google_workspace_group_members(service, args.group_id)

    iam_service = get_aws_iam_identity_center_api_service()

    for member in group_members:
        user_name = member["email"]
        email = member["email"]
        if not args.dry_run:
            create_aws_iam_identity_center_user(iam_service, user_name, email)
        else:
            try:
                iam_service.list_users(UserName=user_name)
                print(
                    "User {} already exists in AWS IAM Identity Center".format(
                        user_name
                    )
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    print(
                        "User {} does not exist in AWS IAM Identity Center".format(
                            user_name
                        )
                    )
                else:
                    raise


if __name__ == "__main__":
    main()
