from __future__ import annotations

from typing import Any


class Replication:
    """Replicates memory data across nodes."""

    def __init__(self):
        self._replication_count: int = 0
        self._replicas: dict[str, dict[str, Any]] = {}

    @property
    def replication_count(self) -> int:
        return self._replication_count

    def replicate(self, data: dict[str, Any], target: str) -> None:
        self._replicas[target] = dict(data)
        self._replication_count += 1

    def get_replica(self, target: str) -> dict[str, Any] | None:
        return self._replicas.get(target)

    def merge(self, local: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
        merged = dict(local)
        for k, v in remote.items():
            if k not in merged:
                merged[k] = v
            elif isinstance(v, dict) and isinstance(merged[k], dict):
                merged[k] = {**merged[k], **v}
        self._replication_count += 1
        return merged

    def list_targets(self) -> list[str]:
        return list(self._replicas.keys())

    def remove_replica(self, target: str) -> bool:
        return self._replicas.pop(target, None) is not None

    def clear(self) -> None:
        self._replicas.clear()
