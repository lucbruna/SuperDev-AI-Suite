from __future__ import annotations

from typing import Any


class DiagramGenerator:
    """Generates ASCII architecture diagrams."""

    def generate_component_diagram(
        self,
        components: list[dict[str, Any]],
    ) -> str:
        if not components:
            return "(no components)"

        lines: list[str] = []
        lines.append("┌────────────────────────────────────────────┐")
        lines.append("│           Component Architecture           │")
        lines.append("├────────────────────────────────────────────┤")

        for comp in components:
            name = comp.get("name", "?")
            resp = comp.get("responsibility", "")
            deps = comp.get("dependencies", [])
            line = f"│  {name:<20} │"
            lines.append(line)
            if resp:
                lines.append(f"│  └─ {resp:<35} │")
            if deps:
                dep_str = ", ".join(str(d) for d in deps[:3])
                if len(deps) > 3:
                    dep_str += "..."
                lines.append(f"│     depends: {dep_str:<30} │")
        lines.append("└────────────────────────────────────────────┘")
        return "\n".join(lines)

    def generate_sequence_diagram(self, steps: list[str]) -> str:
        if not steps:
            return "(no steps)"

        lines: list[str] = []
        lines.append("┌────────── Sequence ──────────┐")
        for i, step in enumerate(steps, 1):
            arrow = "───►" if i % 2 == 1 else "◄───"
            lines.append(f"  {arrow} {step}")
            if i < len(steps):
                lines.append("  │")
        lines.append("└──────────────────────────────┘")
        return "\n".join(lines)

    def generate_flow_diagram(
        self,
        nodes: list[str],
        edges: list[tuple[str, str]],
    ) -> str:
        if not nodes:
            return "(no nodes)"

        lines: list[str] = []
        lines.append("┌────────── Flow Diagram ──────────┐")
        node_markers: dict[str, str] = {}
        for i, node in enumerate(nodes):
            marker = chr(65 + i) if i < 26 else f"N{i}"
            node_markers[node] = marker
            lines.append(f"  [{marker}] {node}")
        if edges:
            lines.append("  ─────────────────────────────")
            for src, dst in edges:
                s = node_markers.get(src, "?")
                d = node_markers.get(dst, "?")
                lines.append(f"  [{s}] ──► [{d}]")
        lines.append("└─────────────────────────────────┘")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "diagram_generator",
            "formats": ["component", "sequence", "flow"],
        }
