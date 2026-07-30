from __future__ import annotations

from typing import Any, Dict, List


class UnsupervisedLearning:
    """Unsupervised learning — clustering and pattern discovery."""

    def __init__(self):
        self._clusters: Dict[str, List[Dict[str, Any]]] = {}
        self._cluster_count: int = 0

    @property
    def clusters(self) -> Dict[str, List[Dict[str, Any]]]:
        return {k: list(v) for k, v in self._clusters.items()}

    @property
    def cluster_count(self) -> int:
        return self._cluster_count

    def cluster(self, items: List[Dict[str, Any]], key: str = "type") -> Dict[str, List[Dict[str, Any]]]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            k = str(item.get(key, "unknown"))
            groups.setdefault(k, []).append(item)
        self._clusters = {k: list(v) for k, v in groups.items()}
        self._cluster_count += 1
        return dict(self._clusters)

    def get_cluster(self, cluster_id: str) -> List[Dict[str, Any]]:
        return list(self._clusters.get(cluster_id, []))

    def cluster_sizes(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self._clusters.items()}

    def clear(self) -> None:
        self._clusters.clear()
        self._cluster_count = 0
