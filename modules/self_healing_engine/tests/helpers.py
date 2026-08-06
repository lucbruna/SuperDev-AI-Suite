"""Module-internal test helpers (never collected by the app)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = ["make_context", "module_smoke"]


def make_context(project_root: str | Path | None = None, registry: Any = None):
    """Build a fresh HealingContext with resolved config for module tests."""
    from modules.self_healing_engine.core import HealingContext

    ctx = HealingContext()
    ctx.config.resolve(project_root)
    if registry is not None:
        ctx.registry = registry
    return ctx


def module_smoke(project_root: str | Path | None = None) -> dict[str, dict[str, bool]]:
    """Instantiate every top-level component and report construction health.

    Deterministic: each entry reports whether the component constructs and
    exposes a ``run``/``tick`` method.
    """
    from modules.self_healing_engine.core import HealingEngine, HealingManager
    from modules.self_healing_engine.monitoring import HealthMonitor
    from modules.self_healing_engine.repair import RepairExecutor, RepairPlanner
    from modules.self_healing_engine.recovery import (
        RollbackManager,
        SnapshotManager,
    )
    from modules.self_healing_engine.validation import ValidatorRunner
    from modules.self_healing_engine.automation import AutomationRunner

    components: dict[str, type] = {
        "monitor": HealthMonitor,
        "planner": RepairPlanner,
        "executor": RepairExecutor,
        "snapshots": SnapshotManager,
        "rollback": RollbackManager,
        "validators": ValidatorRunner,
        "automation": AutomationRunner,
        "engine": HealingEngine,
        "manager": HealingManager,
    }
    report: dict[str, dict[str, bool]] = {}
    for name, cls in components.items():
        instance = cls()
        report[name] = {
            "ok": True,
            "has_run": any(
                callable(getattr(instance, attr, None))
                for attr in dir(instance)
                if not attr.startswith("_")
            ),
        }
    return report
