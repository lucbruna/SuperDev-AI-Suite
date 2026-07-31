from __future__ import annotations

from typing import Any


class ConsistencyChecker:
    """Checks consistency of memory data across replicas."""

    def __init__(self):
        self._checks: int = 0

    @property
    def check_count(self) -> int:
        return self._checks

    def check(self, data: dict[str, Any]) -> bool:
        self._checks += 1
        return isinstance(data, dict)

    def compare(self, local: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
        self._checks += 1
        matching: list[str] = []
        diverging: list[str] = []
        missing_local: list[str] = []
        missing_remote: list[str] = []
        all_keys = set(local.keys()) | set(remote.keys())
        for key in all_keys:
            if key in local and key in remote:
                if local[key] == remote[key]:
                    matching.append(key)
                else:
                    diverging.append(key)
            elif key in local:
                missing_remote.append(key)
            else:
                missing_local.append(key)
        return {
            "consistent": len(diverging) == 0,
            "matching": len(matching),
            "diverging": len(diverging),
            "missing_local": len(missing_local),
            "missing_remote": len(missing_remote),
            "total_keys": len(all_keys),
        }

    def check_consistency(self, replicas: dict[str, dict[str, Any]]) -> dict[str, Any]:
        self._checks += 1
        if len(replicas) < 2:
            return {"consistent": True, "checked": False}
        ids = list(replicas.keys())
        base = replicas[ids[0]]
        for rid in ids[1:]:
            result = self.compare(base, replicas[rid])
            if not result["consistent"]:
                return {"consistent": False, "diverging_replicas": [ids[0], rid]}
        return {"consistent": True}

    def reset(self) -> None:
        self._checks = 0
