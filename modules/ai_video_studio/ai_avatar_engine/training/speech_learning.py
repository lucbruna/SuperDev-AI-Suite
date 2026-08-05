"""Speech learning — learns preferred voice/pacing parameters."""
from __future__ import annotations



class SpeechLearning:
    """Records speech-style feedback (pace, pitch, energy)."""

    def __init__(self) -> None:
        self._pace: list[float] = []
        self._pitch: list[float] = []
        self._energy: list[float] = []

    def record(self, *, pace: float, pitch: float, energy: float) -> None:
        self._pace.append(pace)
        self._pitch.append(pitch)
        self._energy.append(energy)

    def preferred(self) -> dict[str, float]:
        def _avg(values: list[float]) -> float:
            return round(sum(values) / len(values), 3) if values else 0.5

        return {"pace": _avg(self._pace), "pitch": _avg(self._pitch),
                "energy": _avg(self._energy)}


_speech_learning: SpeechLearning | None = None


def get_speech_learning() -> SpeechLearning:
    global _speech_learning
    if _speech_learning is None:
        _speech_learning = SpeechLearning()
    return _speech_learning
