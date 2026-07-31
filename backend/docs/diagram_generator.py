from __future__ import annotations

from pathlib import Path
from typing import Any


class DiagramGenerator:
    def __init__(self):
        self._diagrams: list[dict[str, Any]] = []

    def class_diagram(self, classes: list[dict[str, Any]]) -> str:
        lines = ["```mermaid", "classDiagram"]
        for cls in classes:
            name = cls.get("name", "Unknown")
            lines.append(f"    class {name} {{")
            for method in cls.get("methods", []):
                lines.append(f"        +{method}()")
            lines.append("    }")
        if len(classes) > 1:
            for i in range(len(classes) - 1):
                lines.append(f"    {classes[i]['name']} --> {classes[i + 1]['name']}")
        lines.append("```")
        return "\n".join(lines)

    def flow_diagram(self, nodes: list[dict[str, str]]) -> str:
        lines = ["```mermaid", "graph LR"]
        for i, node in enumerate(nodes):
            node_id = node.get("id", f"n{i}")
            label = node.get("label", node_id)
            lines.append(f"    {node_id}[{label}]")
            if i > 0:
                prev = nodes[i - 1].get("id", f"n{i - 1}")
                lines.append(f"    {prev} --> {node_id}")
        lines.append("```")
        return "\n".join(lines)

    def sequence_diagram(self, participants: list[str], interactions: list[tuple[str, str, str]]) -> str:
        lines = ["```mermaid", "sequenceDiagram"]
        for p in participants:
            lines.append(f"    participant {p}")
        for from_p, to_p, msg in interactions:
            lines.append(f"    {from_p}->>{to_p}: {msg}")
        lines.append("```")
        return "\n".join(lines)

    def component_diagram(self, components: list[dict[str, Any]]) -> str:
        lines = ["```mermaid", "graph TB"]
        for comp in components:
            cid = comp.get("id", "c")
            label = comp.get("label", cid)
            lines.append(f"    subgraph {cid}[{label}]")
            for child in comp.get("children", []):
                child_id = child.get("id", f"{cid}_child")
                child_label = child.get("label", child_id)
                lines.append(f"        {child_id}[{child_label}]")
            lines.append("    end")
            for dep in comp.get("depends_on", []):
                lines.append(f"    {dep} --> {cid}")
        lines.append("```")
        return "\n".join(lines)

    def generate_from_code(self, modules: dict[str, Any]) -> list[str]:
        diagrams = []
        classes_list = []
        for _mod_path, mod_data in modules.items():
            if isinstance(mod_data, dict) and "classes" in mod_data:
                for cls in mod_data["classes"]:
                    classes_list.append(cls)
        if classes_list:
            diagrams.append("## Class Diagram\n" + self.class_diagram(classes_list[:15]) + "\n")
        return diagrams

    def save(self, diagram: str, output_path: str) -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(diagram, encoding="utf-8")
        return str(output_file)
