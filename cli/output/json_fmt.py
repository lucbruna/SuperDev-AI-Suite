"""JSON output formatter for CLI."""

import json


def format_json(data: dict | list, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, default=str)
