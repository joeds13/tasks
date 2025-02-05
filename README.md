# Tasks

Collection of pretty much entirely AI generated scripts for random tasks

## Mise Integration

Uses [mise tasks](https://mise.jdx.dev/tasks/file-tasks.html) to allow `mise run` to find all scripts

All files created need to be executable, so `chmod +x <filename>`

A symlink also needs to exist to map `mise` to these files, so `ln -s <repo location> ~/.config/mise/tasks` eg `ln -s ~/Tasks ~/.config/mise/tasks`

## UV Integration

Follow the [mise uv cookbook](https://mise.jdx.dev/mise-cookbook/python.html#mise-uv) to ensure `mise` and `uv` are integrated

Python is pretty good for wirting these tasks, so using `uv` gives a very portable experience

A simple python script that has imports and a version requirement

`#!/usr/bin/env -S uv run --script` executes the script using `uv` with the `-S` flag allows passing multiple arguments after `env`.
Using `--script` is required if the filename does not end in `.py` (but it's okay if it does as `uv` trims that when listing).

`requires-python = "<=3.13"` sets the python version

`dependencies = ["rich>=13.9.0"]` sets a dependency and version

```python
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
```

```shell
❯ mise run python:print_peps
[python:print_peps] $ ~/.config/mise/tasks/python/print_peps.py
Python version: 3.12.8 (main, Dec 19 2024, 14:22:58) [Clang 18.1.8 ]
[
│   ('1', 'PEP Purpose and Guidelines'),
│   ('2', 'Procedure for Adding New Modules'),
│   ('3', 'Guidelines for Handling Bug Reports'),
│   ('4', 'Deprecation of Standard Modules'),
│   ('5', 'Guidelines for Language Evolution'),
│   ('6', 'Bug Fix Releases'),
│   ('7', 'Style Guide for C Code'),
│   ('8', 'Style Guide for Python Code'),
│   ('9', 'Sample Plaintext PEP Template'),
│   ('10', 'Voting Guidelines')
]
```
