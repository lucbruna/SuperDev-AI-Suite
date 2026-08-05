"""Enterprise Learning — facade over feedback, RL, quality and preferences."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.learning.global_feedback import (
    get_global_feedback,
)
from modules.ai_video_studio.integration.learning.quality_feedback import (
    get_quality_feedback,
)
from modules.ai_video_studio.integration.learning.reinforcement_engine import (
    get_reinforcement_engine,
)
from modules.ai_video_studio.integration.learning.user_preferences import (
    get_user_preferences,
)


class EnterpriseLearningConnector(DomainConnector):
    """Feedback loops, reinforcement learning, quality and preferences."""

    domain = "learning"
    description = "Global feedback, reinforcement learning, quality feedback and user preferences"

    def __init__(self) -> None:
        super().__init__()
        self._register("submit_feedback", lambda d: get_global_feedback().submit(
            d.get("user", "anon"), d.get("sentiment", "neutral"), d.get("message", "")))
        self._register("submit_quality", lambda d: get_quality_feedback().submit(
            d.get("output_type", "video"), d.get("score", 5.0)))
        self._register("choose_option", lambda d: get_reinforcement_engine().choose(d.get("options", [])))
        self._register("reward_option", lambda d: get_reinforcement_engine().reward(
            d.get("option", ""), d.get("value", 1.0)))
        self._register("set_preference", lambda d: get_user_preferences().set(
            d.get("user", "anon"), d.get("key", ""), d.get("value")))
        self._register("learning_summary", lambda d: self._summary())

    def _summary(self) -> dict[str, Any]:
        return {
            "quality": get_quality_feedback().summary(),
            "feedback": get_global_feedback().summary(),
        }


_enterprise_learning_connector: EnterpriseLearningConnector | None = None


def get_enterprise_learning_connector() -> EnterpriseLearningConnector:
    global _enterprise_learning_connector
    if _enterprise_learning_connector is None:
        _enterprise_learning_connector = EnterpriseLearningConnector()
    return _enterprise_learning_connector
