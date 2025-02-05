#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "boto3",
# ]
# ///
import argparse

import boto3


def delete_terratest_policies(dry_run=False):
    iam_client = boto3.client("iam")

    policy_strings_to_delete = ["example"]

    try:
        paginator = iam_client.get_paginator("list_policies")
        for page in paginator.paginate(Scope="Local"):
            for policy in page["Policies"]:
                policy_name = policy["PolicyName"]
                policy_arn = policy["Arn"]
                update_date = policy["UpdateDate"]

                if any(
                    s.lower() in policy_name.lower() for s in policy_strings_to_delete
                ):
                    if dry_run:
                        message = f"Would delete policy: {policy_name} (Last updated: {update_date})"
                        if update_date.year == 2024:
                            print(f"\033[33m{message}\033[0m")  # Orange text
                        else:
                            print(message)
                        continue

                    try:
                        # First detach policy from all entities
                        print(f"Listing entities for policy {policy_arn}")

                        # Check each entity type separately
                        for entity_filter in ["Role", "User", "Group"]:
                            entities = iam_client.list_entities_for_policy(
                                PolicyArn=policy_arn, EntityFilter=entity_filter
                            )

                            # Detach from roles
                            if entity_filter == "Role":
                                for role in entities.get("PolicyRoles", []):
                                    print(
                                        f"Detaching policy from role: {role['RoleName']}"
                                    )
                                    iam_client.detach_role_policy(
                                        RoleName=role["RoleName"], PolicyArn=policy_arn
                                    )

                            # Detach from users
                            elif entity_filter == "User":
                                for user in entities.get("PolicyUsers", []):
                                    print(
                                        f"Detaching policy from user: {user['UserName']}"
                                    )
                                    iam_client.detach_user_policy(
                                        UserName=user["UserName"], PolicyArn=policy_arn
                                    )

                            # Detach from groups
                            elif entity_filter == "Group":
                                for group in entities.get("PolicyGroups", []):
                                    print(
                                        f"Detaching policy from group: {group['GroupName']}"
                                    )
                                    iam_client.detach_group_policy(
                                        GroupName=group["GroupName"],
                                        PolicyArn=policy_arn,
                                    )

                        # Delete all versions except the default
                        print(f"Listing policy versions for {policy_arn}")
                        versions = iam_client.list_policy_versions(PolicyArn=policy_arn)
                        for version in versions["Versions"]:
                            if not version["IsDefaultVersion"]:
                                print(
                                    f"Deleting policy version: {version['VersionId']}"
                                )
                                iam_client.delete_policy_version(
                                    PolicyArn=policy_arn, VersionId=version["VersionId"]
                                )

                        # Delete the policy
                        iam_client.delete_policy(PolicyArn=policy_arn)
                        print(f"Successfully deleted policy: {policy_name}")

                    except iam_client.exceptions.NoSuchEntityException:
                        print(f"Policy {policy_name} not found")
                    except Exception as e:
                        print(f"Error deleting policy {policy_name}: {str(e)}")

    except Exception as e:
        print(f"Error listing policies: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print policies that would be deleted without actually deleting them",
    )
    args = parser.parse_args()
    delete_terratest_policies(dry_run=args.dry_run)
