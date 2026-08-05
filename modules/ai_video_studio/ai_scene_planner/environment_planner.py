"""Environment planner — design the environment/background of a scene."""
from __future__ import annotations

from typing import Any

ENVIRONMENTS = {
    "generic": {"name": "Minimal studio", "props": ["softbox", "cyclorama"], "palette": ["#2c3e50", "#7f8c8d"]},
    "office": {"name": "Modern office", "props": ["desk", "monitors", "plants"], "palette": ["#34495e", "#ecf0f1"]},
    "farm": {"name": "Farm field", "props": ["crops", "horizon", "sun"], "palette": ["#27ae60", "#f1c40f"]},
    "classroom": {"name": "Classroom", "props": ["whiteboard", "desks", "books"], "palette": ["#3498db", "#ecf0f1"]},
    "clinic": {"name": "Medical clinic", "props": ["exam table", "instruments", "white walls"], "palette": ["#e8f8f5", "#1abc9c"]},
    "landscape": {"name": "Scenic viewpoint", "props": ["horizon", "sky", "vegetation"], "palette": ["#1a1a2e", "#16a085"]},
    "lab": {"name": "Laboratory", "props": ["bench", "glassware", "monitors"], "palette": ["#0f3460", "#95a5a6"]},
    "boardroom": {"name": "Boardroom", "props": ["table", "chairs", "screen"], "palette": ["#2c3e50", "#bdc3c7"]},
    "store": {"name": "Storefront", "props": ["shelves", "signage", "products"], "palette": ["#e67e22", "#f39c12"]},
}


class EnvironmentPlanner:
    """Deterministic environment design for scenes."""

    def plan(self, location: str = "generic") -> dict[str, Any]:
        env = ENVIRONMENTS.get(location, ENVIRONMENTS["generic"])
        return {
            "environment": env["name"],
            "props": env["props"],
            "color_palette": env["palette"],
            "backdrop": "cyclorama",
            "depth": "layered",
        }

    def suggest_for_brief(self, brief: str) -> dict[str, Any]:
        text = (brief or "").lower()
        mapping = {
            "office": "office", "escritório": "office", "empresa": "office",
            "fazenda": "farm", "agricultura": "farm", "agro": "farm",
            "escola": "classroom", "curso": "classroom", "educação": "classroom",
            "saúde": "clinic", "medico": "clinic", "clínica": "clinic",
            "turismo": "landscape", "viagem": "landscape",
            "tecnologia": "lab", "tech": "lab",
            "finanças": "boardroom", "financeiro": "boardroom",
            "loja": "store", "e-commerce": "store", "vender": "store",
        }
        for key, env in mapping.items():
            if key in text:
                return self.plan(env)
        return self.plan("generic")

    def list_environments(self) -> list[str]:
        return list(ENVIRONMENTS.keys())


_environment_planner: EnvironmentPlanner | None = None


def get_environment_planner() -> EnvironmentPlanner:
    global _environment_planner
    if _environment_planner is None:
        _environment_planner = EnvironmentPlanner()
    return _environment_planner
