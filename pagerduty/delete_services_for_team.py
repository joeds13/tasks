#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pdpyras",
# ]
# ///
import argparse
import os
import sys

from pdpyras import APISession

ACCESS_TOKEN = os.getenv("PAGERDUTY_TOKEN", False)
TEAM_ID = os.getenv("PAGERDUTY_TEAM_ID", False)


def get_services(session, team_id):
    """Get all services for a team"""
    return list(session.iter_all("services", params={"team_ids[]": team_id}))


def delete_service(session, service_id):
    """Delete a service"""
    session.delete(f"services/{service_id}")


def main():
    parser = argparse.ArgumentParser(description="Delete PagerDuty services in a team")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete services (default is dry run)",
    )
    args = parser.parse_args()

    if not ACCESS_TOKEN:
        print("Please set PAGERDUTY_TOKEN environment variable")
        sys.exit(1)

    session = APISession(ACCESS_TOKEN)
    services = get_services(session, TEAM_ID)

    if not services:
        print("No services found")
        return

    print(f"Found {len(services)} services:")
    for service in services:
        print(f"- {service['name']} ({service['id']})")

    if args.execute:
        print("\nDeleting services...")
        for service in services:
            print(f"Deleting {service['name']}...")
            delete_service(session, service["id"])
        print("Done!")
    else:
        print("\nDry run mode - no services were deleted")
        print("Use --execute flag to actually delete services")


if __name__ == "__main__":
    main()
