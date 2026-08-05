"""Episode generator — structures multi-part video series scripts."""
from __future__ import annotations

from typing import Any


class EpisodeGenerator:
    """Generates an episode plan for a series."""

    def generate(self, topic: str, episode: int = 1) -> dict[str, Any]:
        return {
            "episode": episode,
            "title": f"{topic.title() or 'Série'} — Episódio {episode}",
            "goal": f"Explorar um ângulo de {topic.lower() or 'o tema'} nesta edição.",
        }


_episode_generator: EpisodeGenerator | None = None


def get_episode_generator() -> EpisodeGenerator:
    global _episode_generator
    if _episode_generator is None:
        _episode_generator = EpisodeGenerator()
    return _episode_generator
