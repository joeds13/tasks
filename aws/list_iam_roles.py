#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import boto3


def list_roles_and_tags():
    iam_client = boto3.client("iam")

    try:
        paginator = iam_client.get_paginator("list_roles")
        for page in paginator.paginate():
            for role in page["Roles"]:
                # Skip AWS service-linked roles which start with "AWSServiceRole"
                if (
                    role["RoleName"].startswith("AWSServiceRole")
                    or "aws-service-role" in role["Path"]
                ):
                    continue

                role_name = role["RoleName"]

                # Get tags for the role
                try:
                    tags_response = iam_client.list_role_tags(RoleName=role_name)
                    tags = tags_response["Tags"]

                    # Skip roles with deployed_with = terraform tag
                    terraform_deployed = False
                    for tag in tags:
                        if (
                            tag["Key"] == "deployed_with"
                            and tag["Value"] == "terraform"
                        ):
                            terraform_deployed = True
                            break

                    if terraform_deployed:
                        continue

                    tag_str = (
                        ", ".join([f"{tag['Key']}: {tag['Value']}" for tag in tags])
                        if tags
                        else "No tags found for this role"
                    )
                    print(f"Role: {role_name} | Tags: {tag_str}")

                except iam_client.exceptions.NoSuchEntityException:
                    print(f"Role {role_name} not found")
                except Exception as e:
                    print(f"Error getting tags for role {role_name}: {str(e)}")

    except Exception as e:
        print(f"Error listing roles: {str(e)}")


if __name__ == "__main__":
    list_roles_and_tags()
