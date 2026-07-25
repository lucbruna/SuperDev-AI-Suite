"""YAML output formatter for CLI."""

import yaml


def format_yaml(data: dict | list) -> str:
    return yaml.dump(data, default_flow_style=False, sort_keys=False)
