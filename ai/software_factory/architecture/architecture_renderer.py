"""Renderer for generating architecture documentation and diagrams."""

from typing import Any

from .models import ArchitectureComponent, ArchitectureView, Connector


class ArchitectureRenderer:
    """Generates documentation and diagram representations of architectures."""

    def __init__(self):
        self._formats: list[str] = ["text", "mermaid", "plantuml", "json"]

    def render_text(self, components: list[ArchitectureComponent], connectors: list[Connector]) -> str:
        lines = ["=== Architecture Overview ===\n"]
        lines.append("Components:")
        for c in components:
            lines.append(f"  - {c.name} ({c.component_type.value}): {c.description}")
        lines.append("\nConnectors:")
        for conn in connectors:
            lines.append(f"  - {conn.source_id} -> {conn.target_id} ({conn.connector_type.value})")
        return "\n".join(lines)

    def render_mermaid(self, components: list[ArchitectureComponent], connectors: list[Connector]) -> str:
        lines = ["graph TD"]
        id_map = {c.component_id: c.name.replace(" ", "_") for c in components}
        for c in components:
            lines.append(f"    {id_map[c.component_id]}[{c.name}]")
        for conn in connectors:
            src = id_map.get(conn.source_id, conn.source_id)
            tgt = id_map.get(conn.target_id, conn.target_id)
            lines.append(f"    {src} -->|{conn.connector_type.value}| {tgt}")
        return "\n".join(lines)

    def render_json(self, components: list[ArchitectureComponent], connectors: list[Connector]) -> dict[str, Any]:
        return {
            "components": [{"id": c.component_id, "name": c.name, "type": c.component_type.value} for c in components],
            "connectors": [
                {"id": c.connector_id, "source": c.source_id, "target": c.target_id, "type": c.connector_type.value}
                for c in connectors
            ],
        }

    def render_view(
        self, view: ArchitectureView, components: list[ArchitectureComponent], connectors: list[Connector]
    ) -> str:
        filtered_c = [c for c in components if c.component_id in view.components]
        filtered_conn = [c for c in connectors if c.connector_id in view.connectors]
        header = f"View: {view.name}\nPerspective: {view.perspective}\n"
        return header + self.render_text(filtered_c, filtered_conn)

    def get_supported_formats(self) -> list[str]:
        return list(self._formats)
