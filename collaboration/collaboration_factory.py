"""Factory for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_context import CollaborationContext
from collaboration.collaboration_engine import CollaborationEngine
from collaboration.collaboration_events import CollaborationEvents
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_runtime import CollaborationRuntime
from collaboration.collaboration_security import CollaborationSecurity


def build_engine(
    config: CollaborationConfig | None = None,
    events: CollaborationEvents | None = None,
    metrics: CollaborationMetrics | None = None,
    registry: CollaborationRegistry | None = None,
    security: CollaborationSecurity | None = None,
    context: CollaborationContext | None = None,
    runtime: CollaborationRuntime | None = None,
    **overrides: Any,
) -> CollaborationEngine:
    """Builds a fully wired CollaborationEngine.

    ``overrides`` are merged into the config, e.g.
    ``build_engine(workspace_name="Acme")``.
    """
    if config is None:
        config = CollaborationConfig(**(overrides or {}))
    else:
        config = config.merge(**overrides)
    return CollaborationEngine(
        config=config,
        events=events or CollaborationEvents(),
        metrics=metrics or CollaborationMetrics(),
        registry=registry or CollaborationRegistry(),
        security=security or CollaborationSecurity(),
        context=context or CollaborationContext(),
        runtime=runtime or CollaborationRuntime(),
    )
