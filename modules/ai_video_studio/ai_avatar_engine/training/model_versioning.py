"""Model versioning — versions learned avatar states."""
from __future__ import annotations

import time
from typing import Any


class ModelVersioning:
    """Snapshot/rollback of learned avatar state."""

    def __init__(self) -> None:
        self._versions: dict[str, dict[str, Any]] = {}
        self._current = 0

    def snapshot(self, state: dict[str, Any], *, label: str = "") -> int:
        self._current += 1
        self._versions[str(self._current)] = {
            "version": self._current, "label": label,
            "ts": round(time.time(), 3), "state": dict(state),
        }
        return self._current

    def get(self, version: int | str) -> dict[str, Any] | None:
        v = self._versions.get(str(version))
        return dict(v["state"]) if v else None

    def latest(self) -> dict[str, Any] | None:
        if not self._versions:
            return None
        return dict(self._versions[str(self._current)]["state"])

    def list(self) -> list[dict[str, Any]]:
        return [{"version": v["version"], "label": v["label"], "ts": v["ts"]}
                for v in self._versions.values()]


_model_versioning: ModelVersioning | None = None


def get_model_versioning() -> ModelVersioning:
    global _model_versioning
    if _model_versioning is None:
        _model_versioning = ModelVersioning()
    return _model_versioning
