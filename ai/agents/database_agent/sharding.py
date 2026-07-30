from __future__ import annotations

from typing import Any


class Sharding:
    """Manages database shard distribution."""

    def __init__(self) -> None:
        self._shards: dict[str, dict[str, Any]] = {}

    def add_shard(self, name: str, host: str, weight: int = 1) -> str:
        self._shards[name] = {
            "name": name,
            "host": host,
            "weight": weight,
            "keys_count": 0,
        }
        return name

    def get_shard(self, name: str) -> dict[str, Any] | None:
        return self._shards.get(name)

    def remove_shard(self, name: str) -> bool:
        if name in self._shards:
            del self._shards[name]
            return True
        return False

    def list_shards(self) -> list[dict[str, Any]]:
        return list(self._shards.values())

    @property
    def shard_count(self) -> int:
        return len(self._shards)

    def distribute_data(self, keys: list[str]) -> dict[str, str]:
        shard_names = list(self._shards.keys())
        if not shard_names:
            return {}
        mapping: dict[str, str] = {}
        for key in keys:
            idx = abs(hash(key)) % len(shard_names)
            shard_name = shard_names[idx]
            mapping[key] = shard_name
            if shard_name in self._shards:
                self._shards[shard_name]["keys_count"] += 1
        return mapping

    def rebalance(self) -> dict[str, Any]:
        total_keys = sum(s["keys_count"] for s in self._shards.values())
        if not self._shards or total_keys == 0:
            return {"status": "nothing to rebalance"}
        target = total_keys / len(self._shards)
        moves = 0
        for s in self._shards.values():
            if s["keys_count"] > target + 1:
                moves += int(s["keys_count"] - target)
        return {
            "status": "rebalanced",
            "keys_moved": moves,
            "shards_rebalanced": len(self._shards),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "shards": list(self._shards.values()),
            "shard_count": self.shard_count,
        }
