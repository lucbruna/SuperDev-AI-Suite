from __future__ import annotations

from typing import Any


class Learning:
    """Learning from experiences and memory patterns."""

    def __init__(self):
        self._episodes: list[dict[str, Any]] = []
        self._episode_count: int = 0

    @property
    def episodes(self) -> list[dict[str, Any]]:
        return list(self._episodes)

    @property
    def episode_count(self) -> int:
        return self._episode_count

    def record_episode(self, episode: dict[str, Any]) -> None:
        self._episodes.append(dict(episode))
        self._episode_count += 1

    def learn_from_experience(self, experience: dict[str, Any]) -> dict[str, Any]:
        lesson: dict[str, Any] = {
            "source": experience.get("type", "unknown"),
            "outcome": experience.get("outcome", "neutral"),
            "key_insight": self._extract_insight(experience),
        }
        self.record_episode(lesson)
        return lesson

    def _extract_insight(self, experience: dict[str, Any]) -> str:
        content = experience.get("content", "")
        if isinstance(content, str) and len(content) > 50:
            return content[:50] + "..."
        return str(content)

    def get_lessons_by_outcome(self, outcome: str) -> list[dict[str, Any]]:
        return [e for e in self._episodes if e.get("outcome") == outcome]

    def clear(self) -> None:
        self._episodes.clear()
        self._episode_count = 0
