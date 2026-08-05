"""Voice data models — specs, requests and results for the AI Voice Studio."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VoiceSpec:
    """A named, reusable voice profile."""

    id: str
    name: str
    gender: str = "neutral"  # male | female | neutral | child | elderly
    language: str = "en-US"
    edge_voice: str = ""
    gtts_lang: str = "en"
    rate: float = 1.0          # relative speaking-rate multiplier
    pitch: float = 1.0         # relative pitch multiplier (1.0 = neutral)
    style: list[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "language": self.language,
            "edge_voice": self.edge_voice,
            "gtts_lang": self.gtts_lang,
            "rate": self.rate,
            "pitch": self.pitch,
            "style": list(self.style),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceSpec:
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", data["id"])),
            gender=str(data.get("gender", "neutral")),
            language=str(data.get("language", "en-US")),
            edge_voice=str(data.get("edge_voice", "")),
            gtts_lang=str(data.get("gtts_lang", "en")),
            rate=float(data.get("rate", 1.0)),
            pitch=float(data.get("pitch", 1.0)),
            style=list(data.get("style", [])),
            description=str(data.get("description", "")),
        )


@dataclass
class SynthesisRequest:
    """Parameters for a single synthesis call."""

    text: str
    voice_id: str = "default"
    language: str = "en"
    emotion: str | None = None
    speed: float = 1.0
    pitch: float = 1.0
    output_path: str | None = None


@dataclass
class SynthesisResult:
    """Outcome of a synthesis call (always references a real file)."""

    output_path: str
    duration: float
    engine: str
    voice_id: str
    language: str
    bytes: int = 0
    cached: bool = False
    emotion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_path": self.output_path,
            "duration": self.duration,
            "engine": self.engine,
            "voice_id": self.voice_id,
            "language": self.language,
            "bytes": self.bytes,
            "cached": self.cached,
            "emotion": self.emotion,
        }
