"""Module-internal test helpers (never collected by pytest)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = ["make_context", "module_smoke"]


def make_context(project_root: str | Path | None = None, registry: Any = None):
    """Build a fresh DeveloperContext for module tests.

    Uses a fresh registry by default so no state leaks between tests (the
    module-level default registry persists registrations).
    """
    from modules.autonomous_developer.config import DeveloperConfig
    from modules.autonomous_developer.core import DeveloperContext, DeveloperRegistry

    return DeveloperContext(
        config=DeveloperConfig(project_root=Path(project_root or Path.cwd())),
        registry=registry if registry is not None else DeveloperRegistry(),
    )


def module_smoke(project_root: str | Path | None = None) -> dict[str, dict[str, bool]]:
    """Instantiate every top-level component and report construction health.

    Deterministic: each entry reports whether the component constructs and
    exposes a ``run`` method.
    """
    from modules.autonomous_developer.agents import DeveloperAgent
    from modules.autonomous_developer.generator import CodeGenerator
    from modules.autonomous_developer.planner import ProjectPlanner
    from modules.autonomous_developer.review import CodeReviewer

    components: dict[str, type] = {
        "planner": ProjectPlanner,
        "generator": CodeGenerator,
        "reviewer": CodeReviewer,
        "agent": DeveloperAgent,
    }
    report: dict[str, dict[str, bool]] = {}
    for name, cls in components.items():
        instance = cls()
        report[name] = {
            "ok": True,
            "has_run": callable(getattr(instance, "run", None)),
        }
    return report
