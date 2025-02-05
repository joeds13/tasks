#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import argparse

import boto3


def delete_terratest_roles(dry_run=False):
    iam_client = boto3.client("iam")

    role_strings_to_delete = [
        "example",
    ]

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

                if any(s.lower() in role_name.lower() for s in role_strings_to_delete):
                    if dry_run:
                        role_last_used = (
                            iam_client.get_role(RoleName=role_name)["Role"]
                            .get("RoleLastUsed", {})
                            .get("LastUsedDate", "Never")
                        )
                        print(
                            f"Would delete role: {role_name} (Last used: {role_last_used})"
                        )
                        continue

                    try:
                        # First delete role policies
                        attached_policies = iam_client.list_attached_role_policies(
                            RoleName=role_name
                        )
                        for policy in attached_policies.get("AttachedPolicies", []):
                            iam_client.detach_role_policy(
                                RoleName=role_name, PolicyArn=policy["PolicyArn"]
                            )

                        # Delete inline policies
                        inline_policies = iam_client.list_role_policies(
                            RoleName=role_name
                        )
                        for policy_name in inline_policies.get("PolicyNames", []):
                            iam_client.delete_role_policy(
                                RoleName=role_name, PolicyName=policy_name
                            )

                        # Remove role from instance profiles and delete them
                        instance_profiles = iam_client.list_instance_profiles_for_role(
                            RoleName=role_name
                        )
                        for profile in instance_profiles.get("InstanceProfiles", []):
                            iam_client.remove_role_from_instance_profile(
                                InstanceProfileName=profile["InstanceProfileName"],
                                RoleName=role_name,
                            )
                        for profile in instance_profiles.get("InstanceProfiles", []):
                            iam_client.delete_instance_profile(
                                InstanceProfileName=profile["InstanceProfileName"]
                            )

                        # Delete the role
                        iam_client.delete_role(RoleName=role_name)
                        print(f"Successfully deleted role: {role_name}")

                    except iam_client.exceptions.NoSuchEntityException:
                        print(f"Role {role_name} not found")
                    except Exception as e:
                        print(f"Error deleting role {role_name}: {str(e)}")

    except Exception as e:
        print(f"Error listing roles: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print roles that would be deleted without actually deleting them",
    )
    args = parser.parse_args()
    delete_terratest_roles(dry_run=args.dry_run)
