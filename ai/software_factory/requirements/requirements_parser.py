"""Parser for requirements data from various formats."""
from typing import Any

from .models import Priority, Requirement, RequirementType


class RequirementsParser:
    """Parses requirements from dicts, text, or structured data."""

    def parse(self, data: dict[str, Any]) -> Requirement:
        """Parse a single requirement from a dictionary."""
        rtype_str = data.get("type", "functional")
        try:
            rtype = RequirementType(rtype_str)
        except ValueError:
            rtype = RequirementType.FUNCTIONAL

        prio_str = data.get("priority", "medium")
        try:
            priority = Priority(prio_str)
        except ValueError:
            priority = Priority.MEDIUM

        return Requirement(
            requirement_id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            requirement_type=rtype,
            priority=priority,
            author=data.get("author", ""),
            tags=data.get("tags", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            dependencies=data.get("dependencies", []),
        )

    def parse_many(self, data_list: list[dict[str, Any]]) -> list[Requirement]:
        """Parse multiple requirements."""
        return [self.parse(d) for d in data_list]

    def parse_text(self, text: str) -> Requirement:
        """Parse a simple text-based requirement."""
        lines = text.strip().split("\n")
        title = lines[0] if lines else "Untitled"
        description = "\n".join(lines[1:]) if len(lines) > 1 else ""
        return Requirement(title=title, description=description)

    def parse_yaml_like(self, yaml_str: str) -> list[Requirement]:
        """Parse a simplified YAML-like format."""
        requirements = []
        current: dict[str, Any] = {}
        for line in yaml_str.strip().split("\n"):
            line = line.strip()
            if not line:
                if current:
                    requirements.append(self.parse(current))
                    current = {}
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                current[key.strip()] = val.strip()
        if current:
            requirements.append(self.parse(current))
        return requirements
