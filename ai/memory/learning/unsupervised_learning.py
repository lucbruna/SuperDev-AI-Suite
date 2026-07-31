from __future__ import annotations

from typing import Any


class UnsupervisedLearning:
    """Unsupervised learning — clustering and pattern discovery."""

    def __init__(self):
        self._clusters: dict[str, list[dict[str, Any]]] = {}
        self._cluster_count: int = 0

    @property
    def clusters(self) -> dict[str, list[dict[str, Any]]]:
        return {k: list(v) for k, v in self._clusters.items()}

    @property
    def cluster_count(self) -> int:
        return self._cluster_count

    def cluster(self, items: list[dict[str, Any]], key: str = "type") -> dict[str, list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            k = str(item.get(key, "unknown"))
            groups.setdefault(k, []).append(item)
        self._clusters = {k: list(v) for k, v in groups.items()}
        self._cluster_count += 1
        return dict(self._clusters)

    def get_cluster(self, cluster_id: str) -> list[dict[str, Any]]:
        return list(self._clusters.get(cluster_id, []))

    def cluster_sizes(self) -> dict[str, int]:
        return {k: len(v) for k, v in self._clusters.items()}

    def clear(self) -> None:
        self._clusters.clear()
        self._cluster_count = 0
