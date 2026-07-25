"""Code generator tool for creating boilerplate code."""

import argparse
from pathlib import Path


TEMPLATES = {
    "crud": {
        "model": '''"""{{name}} model."""


class {{name}}:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
''',
        "service": '''"""{{name}} service."""


class {{name}}Service:
    def list(self):
        return []

    def get(self, id: str):
        return None

    def create(self, data: dict):
        return data

    def delete(self, id: str):
        return True
''',
        "router": '''"""{{name}} API router."""


def get_{{name_lower}}_router():
    pass
''',
    }
}


def generate(model_name: str, template: str = "crud", output_dir: str = "."):
    if template not in TEMPLATES:
        print(f"Unknown template: {template}")
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for filename, content in TEMPLATES[template].items():
        code = content.replace("{{name}}", model_name).replace("{{name_lower}}", model_name.lower())
        filepath = out / f"{model_name.lower()}_{filename}.py"
        filepath.write_text(code)
        print(f"Generated: {filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate boilerplate code")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--template", default="crud", choices=list(TEMPLATES.keys()))
    parser.add_argument("--output", default="./generated")
    args = parser.parse_args()

    generate(args.model, args.template, args.output)
