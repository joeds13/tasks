#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pdpyras",
# ]
# ///
import argparse
import os
import sys

from pdpyras import APISession, PDClientError

ACCESS_TOKEN = os.getenv("PAGERDUTY_TOKEN", False)


def get_schedules(session):
    """Get all schedules"""
    return list(session.iter_all("schedules"))


def get_escalation_policies(session):
    """Get all escalation policies"""
    return list(session.iter_all("escalation_policies"))


def get_services_for_policy(session, policy_id):
    """Get all services using an escalation policy"""
    return list(
        session.iter_all("services", params={"escalation_policy_ids[]": [policy_id]})
    )


def remove_escalation_policy_from_service(session, service_id):
    """Remove escalation policy from a service"""
    try:
        service = session.rget(f"services/{service_id}")
        service["escalation_policy"] = None
        session.rput(f"services/{service_id}", json=service)
        return True
    except PDClientError as e:
        print(f"Error removing policy from service {service_id}: {str(e)}")
        return False


def delete_schedule(session, schedule_id):
    """Delete a schedule"""
    try:
        session.delete(f"schedules/{schedule_id}")
        return True
    except PDClientError as e:
        print(f"Error deleting schedule {schedule_id}: {str(e)}")
        return False


def delete_escalation_policy(session, policy_id):
    """Delete an escalation policy"""
    try:
        session.delete(f"escalation_policies/{policy_id}")
        return True
    except PDClientError as e:
        print(f"Error deleting policy {policy_id}: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Delete all PagerDuty schedules and escalation policies"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete items (default is dry run)",
    )
    args = parser.parse_args()

    if not ACCESS_TOKEN:
        print("Please set PAGERDUTY_TOKEN environment variable")
        sys.exit(1)

    session = APISession(ACCESS_TOKEN)
    schedules = get_schedules(session)
    policies = get_escalation_policies(session)

    if not schedules and not policies:
        print("No schedules or escalation policies found")
        return

    print(f"Found {len(schedules)} schedules:")
    for schedule in schedules:
        print(f"- {schedule['name']} ({schedule['id']})")

    print(f"\nFound {len(policies)} escalation policies:")
    for policy in policies:
        print(f"- {policy['name']} ({policy['id']})")

    if args.execute:
        print("\nRemoving services from escalation policies...")
        for policy in policies:
            print(f"Processing policy {policy['name']}...")
            services = get_services_for_policy(session, policy["id"])
            for service in services:
                print(f"Removing policy from service {service['name']}...")
                remove_escalation_policy_from_service(session, service["id"])

        print("\nDeleting escalation policies...")
        success_count = 0
        for policy in policies:
            print(f"Deleting policy {policy['name']}...")
            if delete_escalation_policy(session, policy["id"]):
                success_count += 1
        print(f"Successfully deleted {success_count} of {len(policies)} policies")

        print("\nDeleting schedules...")
        success_count = 0
        for schedule in schedules:
            print(f"Deleting schedule {schedule['name']}...")
            if delete_schedule(session, schedule["id"]):
                success_count += 1
        print(f"Successfully deleted {success_count} of {len(schedules)} schedules")
        print("Done!")
    else:
        print("\nDry run mode - nothing was deleted")
        print("Use --execute flag to actually delete items")


if __name__ == "__main__":
    main()
