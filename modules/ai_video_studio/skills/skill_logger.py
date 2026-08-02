"""Skill logger — structured activity log backed by the Vol 10 integration logger."""
from __future__ import annotations
from typing import Any


class SkillLogger:
    def log(
        self,
        service: str,
        message: str,
        *,
        level: str = "info",
        payload: dict[str, Any] | None = None,
    ) -> None:
        try:
            from modules.ai_video_studio.integration.integration_logger import (
                get_integration_logger,
            )

            get_integration_logger().log(
                f"skills.{service}", message, level=level, payload=payload or {}
            )
        except Exception:  # noqa: BLE001 — logging must never break skill flow
            return


_skill_logger: SkillLogger | None = None


def get_skill_logger() -> SkillLogger:
    global _skill_logger
    if _skill_logger is None:
        _skill_logger = SkillLogger()
    return _skill_logger
