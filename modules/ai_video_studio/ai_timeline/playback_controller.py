"""Playback controller — play/pause/seek state for the timeline preview."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class PlaybackController:
    """Controls playback state: position, play/pause, speed, looping."""

    def __init__(self, engine: Any | None = None) -> None:
        if engine is None:
            from modules.ai_video_studio.ai_timeline.timeline_engine import get_timeline_engine

            engine = get_timeline_engine()
        self.engine = engine
        self.position: float = 0.0
        self.playing: bool = False
        self.speed: float = 1.0
        self.loop: bool = False

    def play(self) -> dict[str, Any]:
        self.playing = True
        return self.state()

    def pause(self) -> dict[str, Any]:
        self.playing = False
        return self.state()

    def toggle(self) -> dict[str, Any]:
        self.playing = not self.playing
        return self.state()

    def seek(self, position: float) -> dict[str, Any]:
        if position < 0:
            raise ValidationError("Position cannot be negative", field="position")
        self.position = position
        return self.state()

    def set_speed(self, speed: float) -> dict[str, Any]:
        if speed <= 0:
            raise ValidationError("Speed must be positive", field="speed")
        self.speed = speed
        return self.state()

    def set_loop(self, loop: bool) -> dict[str, Any]:
        self.loop = loop
        return self.state()

    def step(self, delta: float) -> dict[str, Any]:
        """Advance playback by delta seconds (respecting loop and duration)."""
        duration = self.engine.duration()
        self.position += delta * self.speed
        if duration > 0:
            if self.loop:
                self.position = self.position % duration
            else:
                self.position = min(self.position, duration)
                if self.position >= duration:
                    self.playing = False
        return self.state()

    def state(self) -> dict[str, Any]:
        return {
            "position": round(self.position, 3),
            "playing": self.playing,
            "speed": self.speed,
            "loop": self.loop,
            "duration": round(self.engine.duration(), 3),
        }


_playback_controller: PlaybackController | None = None


def get_playback_controller() -> PlaybackController:
    global _playback_controller
    if _playback_controller is None:
        _playback_controller = PlaybackController()
    return _playback_controller
