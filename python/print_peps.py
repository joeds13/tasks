#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "<=3.13"
# dependencies = ["httpx", "rich>=13.9.0"]
# ///
import sys

import httpx
from rich.pretty import pprint

resp = httpx.get("https://peps.python.org/api/peps.json")
data = resp.json()

print(f"Python version: {sys.version}")
pprint([(k, v["title"]) for k, v in data.items()][:10])
