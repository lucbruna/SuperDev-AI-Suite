"""Generator for README files."""
from typing import Any


class ReadmeGenerator:
    """Generates README.md files for projects."""

    def __init__(self):
        self._sections: list[str] = ["title", "description", "installation", "usage", "contributing", "license"]

    def generate(self, project_info: dict[str, Any]) -> str:
        name = project_info.get("name", "Project")
        description = project_info.get("description", "")
        installation = project_info.get("installation", "pip install .")
        usage = project_info.get("usage", "")
        license_name = project_info.get("license", "MIT")

        lines = [
            f"# {name}",
            "",
            description,
            "",
            "## Installation",
            "",
            f"```bash\n{installation}\n```",
            "",
            "## Usage",
            "",
            usage or f"```python\nimport {name.lower().replace(' ', '_')}\n```",
            "",
            "## Contributing",
            "",
            "Contributions are welcome!",
            "",
            "## License",
            "",
            f"This project is licensed under the {license_name} License.",
        ]
        return "\n".join(lines)

    def get_sections(self) -> list[str]:
        return list(self._sections)
