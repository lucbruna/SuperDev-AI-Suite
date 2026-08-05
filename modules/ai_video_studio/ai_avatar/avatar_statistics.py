"""Avatar statistics — track presenter render metrics."""
from __future__ import annotations

import statistics
import time
from typing import Any


class AvatarStatistics:
    """Counts renders by actor/scene and tracks render durations."""

    def __init__(self) -> None:
        self._started = time.time()
        self._by_actor: dict[str, int] = {}
        self._by_scene: dict[str, int] = {}
        self._durations: list[float] = []

    def record(self, *, actor_id: str, scene_type: str, duration_ms: float) -> None:
        self._by_actor[actor_id] = self._by_actor.get(actor_id, 0) + 1
        self._by_scene[scene_type] = self._by_scene.get(scene_type, 0) + 1
        self._durations.append(duration_ms)

    def summary(self) -> dict[str, Any]:
        return {
            "uptime_seconds": round(time.time() - self._started, 2),
            "total": sum(self._by_actor.values()),
            "by_actor": dict(self._by_actor),
            "by_scene": dict(self._by_scene),
            "avg_render_ms": round(statistics.mean(self._durations), 2) if self._durations else 0.0,
        }

    def reset(self) -> None:
        self.__init__()


_avatar_statistics: AvatarStatistics | None = None


def get_avatar_statistics() -> AvatarStatistics:
    global _avatar_statistics
    if _avatar_statistics is None:
        _avatar_statistics = AvatarStatistics()
    return _avatar_statistics
