"""Shared test helpers for the Super AI Orchestrator Core."""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.api import OrchestratorAPI
from modules.super_ai_orchestrator.config import KernelConfig
from modules.super_ai_orchestrator.core.task import Task


def make_task(
    kind: str = "develop",
    title: str = "test task",
    payload: dict[str, Any] | None = None,
    priority: int = 5,
    **overrides: Any,
) -> Task:
    """Deterministic task fixture."""
    fields: dict[str, Any] = {
        "kind": kind,
        "title": title,
        "payload": payload or {},
        "priority": priority,
    }
    fields.update(overrides)
    return Task(**fields)


def make_api(governance: bool = False) -> OrchestratorAPI:
    """Facade with governance off so tests run end-to-end deterministically."""
    return OrchestratorAPI(kernel_config=KernelConfig(governance_required=governance))
