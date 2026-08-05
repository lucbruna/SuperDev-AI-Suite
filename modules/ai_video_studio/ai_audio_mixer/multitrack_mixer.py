"""Multitrack Mixer — DAW-style track control before the master bus.

Tracks have ``gain`` (fader), ``mute``, ``solo``, ``pan`` and an optional
``bus`` group (all tracks in a bus share its level).
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_audio_mixer.mixer_engine import get_mixer_engine


class MultitrackMixer:
    """Controls a session of tracks and mixes them through the engine."""

    def __init__(self) -> None:
        self._tracks: list[dict[str, Any]] = []
        self._engine = get_mixer_engine()

    def add_track(self, samples: Any, *, name: str = "", gain: float = 1.0,
                  pan: float = 0.0, bus: str | None = None, eq: list | None = None) -> str:
        track = {"name": name or f"track_{len(self._tracks) + 1}", "samples": samples,
                 "gain": gain, "pan": pan, "bus": bus, "eq": eq or [],
                 "mute": False, "solo": False}
        self._tracks.append(track)
        return track["name"]

    def set_fader(self, name: str, gain: float) -> None:
        for track in self._tracks:
            if track["name"] == name:
                track["gain"] = max(0.0, gain)

    def set_mute(self, name: str, muted: bool) -> None:
        for track in self._tracks:
            if track["name"] == name:
                track["mute"] = muted

    def set_solo(self, name: str, solo: bool) -> None:
        for track in self._tracks:
            track["solo"] = track["name"] == name if solo else False

    def mix(self, *, output_path: str | None = None) -> dict[str, Any]:
        any_solo = any(t["solo"] for t in self._tracks)
        active = [
            t for t in self._tracks
            if not t["mute"] and (not any_solo or t["solo"])
        ]
        return self._engine.mix(active, output_path=output_path)
