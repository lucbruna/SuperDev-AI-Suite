from typing import Any, Optional
import uuid
from datetime import datetime


class SpeakerIdentifier:
    def __init__(self) -> None:
        self._enrolled_speakers: dict[str, dict[str, Any]] = {}
        self._max_profiles = 100

    async def identify_speaker(self, audio_sample: bytes) -> dict[str, Any]:
        best_match: Optional[str] = None
        best_score = 0.0
        for speaker_id, profile in self._enrolled_speakers.items():
            score = self._compute_similarity(audio_sample, profile["voice_print"])
            if score > best_score:
                best_score = score
                best_match = speaker_id
        if best_match and best_score > 0.5:
            profile = self._enrolled_speakers[best_match]
            return {
                "identified": True,
                "speaker_id": best_match,
                "speaker_name": profile["name"],
                "confidence": round(best_score, 3),
                "timestamp": datetime.now().isoformat(),
            }
        return {
            "identified": False,
            "speaker_id": None,
            "speaker_name": None,
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    async def enroll_speaker(self, name: str, audio_sample: bytes, metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        if len(self._enrolled_speakers) >= self._max_profiles:
            return {"error": "Maximum number of enrolled speakers reached."}
        speaker_id = str(uuid.uuid4())
        voice_print = self._generate_voice_print(audio_sample)
        profile: dict[str, Any] = {
            "speaker_id": speaker_id,
            "name": name,
            "voice_print": voice_print,
            "enrolled_at": datetime.now().isoformat(),
            "samples_enrolled": 1,
            "metadata": metadata or {},
        }
        self._enrolled_speakers[speaker_id] = profile
        return {
            "speaker_id": speaker_id,
            "name": name,
            "status": "enrolled",
            "voice_print_size": len(voice_print),
        }

    async def verify_speaker(self, speaker_id: str, audio_sample: bytes) -> dict[str, Any]:
        profile = self._enrolled_speakers.get(speaker_id)
        if not profile:
            return {"verified": False, "reason": "Speaker not found"}
        score = self._compute_similarity(audio_sample, profile["voice_print"])
        verified = score > 0.65
        return {
            "verified": verified,
            "speaker_id": speaker_id,
            "speaker_name": profile["name"],
            "confidence": round(score, 3),
            "threshold": 0.65,
        }

    def get_speaker_profile(self, speaker_id: str) -> Optional[dict[str, Any]]:
        profile = self._enrolled_speakers.get(speaker_id)
        if profile:
            result = dict(profile)
            result.pop("voice_print", None)
            return result
        return None

    def list_enrolled_speakers(self) -> list[dict[str, Any]]:
        return [
            {
                "speaker_id": sid,
                "name": p["name"],
                "enrolled_at": p["enrolled_at"],
                "samples_enrolled": p["samples_enrolled"],
            }
            for sid, p in self._enrolled_speakers.items()
        ]

    def _generate_voice_print(self, audio_sample: bytes) -> list[float]:
        import hashlib
        digest = hashlib.sha256(audio_sample).digest()
        return [b / 255.0 for b in digest[:32]]

    def _compute_similarity(self, audio_sample: bytes, voice_print: list[float]) -> float:
        import hashlib
        sample_print = self._generate_voice_print(audio_sample)
        if len(sample_print) != len(voice_print):
            return 0.0
        dot = sum(a * b for a, b in zip(sample_print, voice_print))
        norm1 = sum(a * a for a in sample_print) ** 0.5
        norm2 = sum(b * b for b in voice_print) ** 0.5
        if norm1 * norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
