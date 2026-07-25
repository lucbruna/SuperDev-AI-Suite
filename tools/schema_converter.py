"""Schema converter tool for converting between formats."""

import argparse
import json
from pathlib import Path


def openapi_to_jsonschema(openapi_path: str) -> dict:
    """Convert OpenAPI schema to JSON Schema."""
    with open(openapi_path) as f:
        openapi = json.load(f)

    schemas = openapi.get("components", {}).get("schemas", {})
    return {"type": "object", "properties": schemas}


def json_to_typescript(schema: dict, name: str = "Interface") -> str:
    """Convert JSON Schema to TypeScript interface."""
    props = schema.get("properties", {})
    lines = [f"export interface {name} {{"]
    for prop_name, prop_schema in props.items():
        prop_type = prop_schema.get("type", "any")
        ts_type = {"string": "string", "integer": "number", "number": "number", "boolean": "boolean"}.get(prop_type, "any")
        lines.append(f"  {prop_name}: {ts_type};")
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert schemas between formats")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", choices=["jsonschema", "typescript"], default="jsonschema")
    args = parser.parse_args()

    if args.format == "jsonschema":
        result = openapi_to_jsonschema(args.input)
    else:
        with open(args.input) as f:
            schema = json.load(f)
        result = json_to_typescript(schema)

    output = Path(args.output)
    if isinstance(result, dict):
        output.write_text(json.dumps(result, indent=2))
    else:
        output.write_text(str(result))

    print(f"Converted: {args.output}")
