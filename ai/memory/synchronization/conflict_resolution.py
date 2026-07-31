from __future__ import annotations

from typing import Any


class ConflictResolution:
    """Detects and resolves conflicts between memory states."""

    def __init__(self):
        self._conflicts_resolved: int = 0

    @property
    def conflicts_resolved(self) -> int:
        return self._conflicts_resolved

    def detect(self, local: dict[str, Any], remote: dict[str, Any]) -> list[dict[str, Any]]:
        conflicts: list[dict[str, Any]] = []
        for key in set(local.keys()) & set(remote.keys()):
            if local[key] != remote[key]:
                conflicts.append(
                    {
                        "key": key,
                        "local_value": local[key],
                        "remote_value": remote[key],
                    }
                )
        return conflicts

    def resolve(
        self, data: dict[str, Any], conflicts: list[dict[str, Any]], strategy: str = "last_write"
    ) -> dict[str, Any]:

        resolved = dict(data)
        for conflict in conflicts:
            key = conflict["key"]
            if strategy == "local":
                resolved[key] = conflict["local_value"]
            elif strategy == "remote":
                resolved[key] = conflict["remote_value"]
            else:
                resolved[key] = conflict.get("remote_value", conflict["local_value"])
            self._conflicts_resolved += 1
        return resolved

    def resolve_all(
        self, local: dict[str, Any], remote: dict[str, Any], strategy: str = "last_write"
    ) -> dict[str, Any]:
        conflicts = self.detect(local, remote)
        return self.resolve({**local, **remote}, conflicts, strategy)

    def stats(self) -> dict[str, Any]:
        return {"conflicts_resolved": self._conflicts_resolved}

    def clear(self) -> None:
        self._conflicts_resolved = 0
