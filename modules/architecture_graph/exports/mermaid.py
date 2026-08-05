"""Mermaid flowchart export (renders in GitHub, Notion, docs)."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def _mm_id(node_id: str) -> str:
    """Mermaid node ids must be alphanumeric; map and keep a label map."""
    safe = "".join(c if c.isalnum() else "_" for c in node_id)
    return safe or "n"


def to_mermaid(graph: ArchitectureGraph) -> str:
    lines = ["flowchart LR"]
    for node in graph.nodes():
        label = node.name.replace('"', "&quot;").replace("\n", " ")
        lines.append(f'  {_mm_id(node.id)}["{label}"]:::k{node.kind}')
    for edge in graph.edges():
        lines.append(f"  {_mm_id(edge.source)} -->|{edge.kind}| {_mm_id(edge.target)}")
    lines.append("")
    lines.append("classDef kfile fill:#64748b22,stroke:#64748b;")
    lines.append("classDef kmodule fill:#3b82f622,stroke:#3b82f6;")
    lines.append("classDef kpackage fill:#8b5cf622,stroke:#8b5cf6;")
    lines.append("classDef kapi fill:#f59e0b22,stroke:#f59e0b;")
    lines.append("classDef kagent fill:#10b98122,stroke:#10b981;")
    lines.append("classDef kplugin fill:#ef444422,stroke:#ef4444;")
    lines.append("classDef kworkflow fill:#06b6d422,stroke:#06b6d4;")
    return "\n".join(lines) + "\n"


def to_dict(graph: ArchitectureGraph) -> dict[str, Any]:
    return {"format": "mermaid", "source": to_mermaid(graph)}
