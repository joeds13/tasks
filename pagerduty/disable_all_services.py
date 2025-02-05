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


def get_services(session):
    """Get all services"""
    return list(session.iter_all("services"))


def disable_service(session, service_id):
    """Disable a service"""
    session.put(f"services/{service_id}", json={"service": {"status": "disabled"}})


def main():
    parser = argparse.ArgumentParser(description="Disable all PagerDuty services")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually disable services (default is dry run)",
    )
    args = parser.parse_args()

    if not ACCESS_TOKEN:
        print("Please set PAGERDUTY_TOKEN environment variable")
        sys.exit(1)

    session = APISession(ACCESS_TOKEN)
    services = get_services(session)

    if not services:
        print("No services found")
        return

    print(f"Found {len(services)} services:")
    for service in services:
        print(f"- {service['name']} ({service['id']})")

    if args.execute:
        print("\nDisabling services...")
        for service in services:
            print(f"Disabling {service['name']}...")
            disable_service(session, service["id"])
        print("Done!")
    else:
        print("\nDry run mode - no services were disabled")
        print("Use --execute flag to actually disable services")


if __name__ == "__main__":
    main()
