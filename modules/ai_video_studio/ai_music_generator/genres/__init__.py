"""Genres — 20 music genres with real chord progressions and instrumentation."""
from __future__ import annotations

from modules.ai_video_studio.ai_music_generator.genres import (
    cinematic, orchestral, electronic, rock, pop, jazz, blues, country, lofi,
    trap, hiphop, gospel, ambient, meditation, podcast, corporate, agriculture,
    suspense, horror, adventure,
)

_REGISTRY: dict[str, dict] = {
    "cinematic": cinematic.GENRE,
    "orchestral": orchestral.GENRE,
    "electronic": electronic.GENRE,
    "rock": rock.GENRE,
    "pop": pop.GENRE,
    "jazz": jazz.GENRE,
    "blues": blues.GENRE,
    "country": country.GENRE,
    "lofi": lofi.GENRE,
    "trap": trap.GENRE,
    "hiphop": hiphop.GENRE,
    "gospel": gospel.GENRE,
    "ambient": ambient.GENRE,
    "meditation": meditation.GENRE,
    "podcast": podcast.GENRE,
    "corporate": corporate.GENRE,
    "agriculture": agriculture.GENRE,
    "suspense": suspense.GENRE,
    "horror": horror.GENRE,
    "adventure": adventure.GENRE,
}


def get_genre(name: str) -> dict:
    """Return the genre spec dict (falls back to ambient)."""
    return _REGISTRY.get(name.lower().strip(), ambient.GENRE)


def list_genres() -> list[str]:
    return sorted(_REGISTRY)
