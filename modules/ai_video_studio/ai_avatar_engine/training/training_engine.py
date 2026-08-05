"""Training engine — orchestrates all avatar learning subsystems."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.training.facial_learning import (
    get_facial_learning,
)
from modules.ai_video_studio.ai_avatar_engine.training.gesture_learning import (
    get_gesture_learning,
)
from modules.ai_video_studio.ai_avatar_engine.training.identity_learning import (
    get_identity_learning,
)
from modules.ai_video_studio.ai_avatar_engine.training.model_versioning import (
    get_model_versioning,
)
from modules.ai_video_studio.ai_avatar_engine.training.movement_learning import (
    get_movement_learning,
)
from modules.ai_video_studio.ai_avatar_engine.training.quality_validation import (
    get_quality_validation,
)
from modules.ai_video_studio.ai_avatar_engine.training.reinforcement_learning import (
    get_reinforcement_learning,
)
from modules.ai_video_studio.ai_avatar_engine.training.speech_learning import (
    get_speech_learning,
)


class TrainingEngine:
    """Aggregates the avatar training subsystems."""

    def __init__(self) -> None:
        self.identity = get_identity_learning()
        self.speech = get_speech_learning()
        self.gestures = get_gesture_learning()
        self.facial = get_facial_learning()
        self.movement = get_movement_learning()
        self.rl = get_reinforcement_learning()
        self.quality = get_quality_validation()
        self.versions = get_model_versioning()

    def record_feedback(self, *, profile_id: str | None = None, gesture: str | None = None,
                        emotion: str | None = None, movement: str | None = None,
                        score: float) -> None:
        """Record a feedback score across any applicable learning axes."""
        if profile_id:
            self.identity.record(profile_id, score)
        if gesture:
            self.gestures.record(gesture, score)
        if emotion:
            self.facial.record(emotion, score)
        if movement:
            self.movement.record(movement, score)

    def validate(self, descriptor: dict[str, Any]) -> dict[str, Any]:
        return self.quality.score(descriptor)

    def choose_action(self, actions: list[str]) -> str:
        return self.rl.choose(actions)

    def snapshot_state(self) -> int:
        state = {
            "identity": self.identity.report(),
            "gestures": self.gestures.report(),
            "facial": self.facial.report(),
            "movement": self.movement.report(),
            "rl": self.rl.stats(),
        }
        return self.versions.snapshot(state, label="training_state")

    def summary(self) -> dict[str, Any]:
        return {
            "identity": self.identity.report(),
            "gestures": self.gestures.report(),
            "facial": self.facial.report(),
            "movement": self.movement.report(),
            "speech": self.speech.preferred(),
            "versions": self.versions.list(),
        }


_training_engine: TrainingEngine | None = None


def get_training_engine() -> TrainingEngine:
    """Return the shared training engine singleton."""
    global _training_engine
    if _training_engine is None:
        _training_engine = TrainingEngine()
    return _training_engine
