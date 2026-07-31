"""Voice - Voice recognition module."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Voiceprint:
    voiceprint_id: str
    user_id: str
    embedding: list[float] = field(default_factory=list)
    duration_seconds: float = 0.0
    quality: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True


class VoiceRecognitionManager:
    def __init__(self):
        self.voiceprints: dict[str, Voiceprint] = {}
        self.recognition_log: list[dict[str, Any]] = []

    def enroll(
        self, user_id: str, embedding: list[float] = None, duration: float = 0.0, quality: float = 0.0
    ) -> Voiceprint:
        vp_id = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        vp = Voiceprint(
            voiceprint_id=vp_id, user_id=user_id, embedding=embedding or [], duration_seconds=duration, quality=quality
        )
        self.voiceprints[vp_id] = vp
        return vp

    def verify(self, user_id: str, probe_embedding: list[float] = None, threshold: float = 0.8) -> bool:
        for vp in self.voiceprints.values():
            if vp.user_id == user_id and vp.active and vp.embedding and probe_embedding:
                score = (
                    sum(a * b for a, b in zip(vp.embedding, probe_embedding, strict=False))
                    / (sum(a**2 for a in vp.embedding) ** 0.5 * sum(b**2 for b in probe_embedding) ** 0.5)
                    if probe_embedding
                    else 0
                )
                self.recognition_log.append(
                    {"user_id": user_id, "score": score, "timestamp": datetime.now().isoformat()}
                )
                return score >= threshold
        return False

    def identify(self, probe_embedding: list[float] = None, threshold: float = 0.8) -> str | None:
        best_match = None
        best_score = 0.0
        for vp in self.voiceprints.values():
            if not vp.active or not vp.embedding or not probe_embedding:
                continue
            score = (
                sum(a * b for a, b in zip(vp.embedding, probe_embedding, strict=False))
                / (sum(a**2 for a in vp.embedding) ** 0.5 * sum(b**2 for b in probe_embedding) ** 0.5)
                if probe_embedding
                else 0
            )
            if score > best_score and score >= threshold:
                best_score = score
                best_match = vp.user_id
        return best_match

    def get_user_voiceprints(self, user_id: str) -> list[Voiceprint]:
        return [vp for vp in self.voiceprints.values() if vp.user_id == user_id and vp.active]

    def remove(self, voiceprint_id: str) -> bool:
        if voiceprint_id in self.voiceprints:
            self.voiceprints[voiceprint_id].active = False
            return True
        return False

    def count(self) -> int:
        return len([vp for vp in self.voiceprints.values() if vp.active])
