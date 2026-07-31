"""Context for an orchestration run (Volume 31)."""

from __future__ import annotations

import time
from typing import Any


class OrchestratorContext:
    """Session-level metadata shared across agents and subsystems."""

    def __init__(self, run_id: str = "", project: str = "",
                 organization: str = "", owner: str = "") -> None:
        self.run_id = run_id
        self.project = project
        self.organization = organization
        self.owner = owner
        self.started_at = time.time()
        self.metadata: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "project": self.project,
            "organization": self.organization,
            "owner": self.owner,
            "started_at": self.started_at,
            "metadata": dict(self.metadata),
        }
