"""Model router — route generation requests to the best available model."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import AIError


class ModelRouter:
    """Selects a model for a request based on mode, hardware and policy."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = [
            {"mode": "text_to_video", "model": "wan", "min_gpu_mb": 8000},
            {"mode": "image_to_video", "model": "image_to_video", "min_gpu_mb": 8000},
            {"mode": "video_to_video", "model": "video_to_video", "min_gpu_mb": 6000},
        ]

    def route(
        self,
        *,
        mode: str,
        available_models: list[str],
        gpu_memory_mb: int = 0,
        quality_profile: str = "balanced",
    ) -> str:
        rule = next((r for r in self._rules if r["mode"] == mode), None)
        if rule is None:
            raise AIError(f"No routing rule for mode '{mode}'")
        if gpu_memory_mb >= rule["min_gpu_mb"] and rule["model"] in available_models:
            return rule["model"]
        # CPU fallback — pick the lightest compatible model.
        fallback = self._fallback_for(mode, available_models)
        if fallback is None:
            raise AIError(f"No available model for mode '{mode}'")
        return fallback

    def _fallback_for(self, mode: str, available_models: list[str]) -> str | None:
        priority = ["tiny", "small", "base", "cpu"]
        for candidate in priority:
            if any(candidate in m for m in available_models):
                return next(m for m in available_models if candidate in m)
        return available_models[0] if available_models else None

    def add_rule(self, mode: str, model: str, min_gpu_mb: int) -> None:
        self._rules.append({"mode": mode, "model": model, "min_gpu_mb": min_gpu_mb})


_model_router: ModelRouter | None = None


def get_model_router() -> ModelRouter:
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
