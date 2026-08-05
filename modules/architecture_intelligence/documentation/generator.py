"""Documentation generator: produces architecture documentation from a graph.

Markdown output combining graph stats, dependency health, and insights.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class DocumentationGenerator:
    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def generate(self, title: str = "Architecture Documentation") -> dict[str, Any]:
        graph = self.engine.graph(build_if_missing=True)
        stats = graph.stats()
        insights = self.engine.insights().get("insights", [])

        lines = [
            f"# {title}",
            "",
            f"_Generated {datetime.now(timezone.utc).isoformat()} by SuperDev architecture_intelligence_",
            "",
            "## Overview",
            "",
            f"- **Nodes:** {stats.get('nodes', 0)}",
            f"- **Edges:** {stats.get('edges', 0)}",
            f"- **Packages:** {stats.get('packages', 0)}",
            "",
            "## Structure",
            "",
        ]
        for package in sorted(stats.get("packages_by_name", {}).keys()):
            lines.append(f"- `{package}`")

        if insights:
            lines.extend(["", "## Insights", ""])
            for item in insights:
                lines.append(f"- [{item.get('kind', 'info')}] {item.get('message', '')}")

        markdown = "\n".join(lines)
        return {
            "title": title,
            "format": "markdown",
            "source": "architecture_intelligence.documentation",
            "content": markdown,
            "stats": stats,
        }


def generate_documentation(engine: Any, title: str = "Architecture Documentation") -> dict[str, Any]:
    return DocumentationGenerator(engine).generate(title)
