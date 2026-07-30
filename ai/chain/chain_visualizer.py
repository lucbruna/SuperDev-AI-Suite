from __future__ import annotations

from typing import Any


class ChainVisualizer:
    """Generates visual representations of reasoning chains."""

    def __init__(self) -> None:
        self._formats: dict[str, Any] = {}

    def register_format(self, name: str, formatter: Any) -> None:
        self._formats[name] = formatter

    async def visualize(self, chain: dict[str, Any], fmt: str = "text") -> str:
        steps = chain.get("steps", [])
        if fmt == "mermaid":
            return self._to_mermaid(steps)
        return self._to_text(steps)

    def _to_text(self, steps: list[dict[str, Any]]) -> str:
        lines = ["Reasoning Chain:"]
        for i, step in enumerate(steps, 1):
            lines.append(f"  {i}. [{step.get('type', '?')}] {step.get('description', '')}")
        return "\n".join(lines)

    def _to_mermaid(self, steps: list[dict[str, Any]]) -> str:
        lines = ["graph TD"]
        for i, step in enumerate(steps):
            node_id = step.get("id", f"s{i}")
            label = step.get("type", "?").replace('"', "'")
            lines.append(f'  {node_id}["{label}: {step.get("description", "")}"]')
            if i > 0:
                prev = steps[i - 1].get("id", f"s{i-1}")
                lines.append(f"  {prev} --> {node_id}")
        return "\n".join(lines)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        chain = context.get("chain", {})
        fmt = context.get("format", "text")
        viz = await self.visualize(chain, fmt)
        return {"visualization": viz, "format": fmt}
