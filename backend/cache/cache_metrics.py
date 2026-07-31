from collections import defaultdict


class CacheMetrics:
    def __init__(self) -> None:
        self._hits: dict[str, int] = defaultdict(int)
        self._misses: dict[str, int] = defaultdict(int)

    def _get_prefix(self, key: str) -> str:
        if ":" in key:
            return key.split(":")[1] if key.count(":") >= 2 else key
        return key

    def track_hit(self, key: str) -> None:
        prefix = self._get_prefix(key)
        self._hits[prefix] += 1

    def track_miss(self, key: str) -> None:
        prefix = self._get_prefix(key)
        self._misses[prefix] += 1

    def get_hit_rate(self) -> float:
        total_hits = sum(self._hits.values())
        total_misses = sum(self._misses.values())
        total = total_hits + total_misses
        if total == 0:
            return 0.0
        return round(total_hits / total, 4)

    def get_miss_rate(self) -> float:
        total_hits = sum(self._hits.values())
        total_misses = sum(self._misses.values())
        total = total_hits + total_misses
        if total == 0:
            return 0.0
        return round(total_misses / total, 4)

    def get_stats(self) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        all_prefixes = set(self._hits.keys()) | set(self._misses.keys())
        for prefix in all_prefixes:
            result[prefix] = {
                "hits": self._hits.get(prefix, 0),
                "misses": self._misses.get(prefix, 0),
            }
        return result

    def reset(self) -> None:
        self._hits.clear()
        self._misses.clear()
