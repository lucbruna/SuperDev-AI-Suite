"""Image engine — top-level orchestrator for AI image generation."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class ImageEngine:
    """Generates images by routing prompts to style-specific generators."""

    def __init__(self) -> None:
        self._requests: dict[str, dict[str, Any]] = {}

    def generate(
        self,
        prompt: str,
        *,
        style: str = "realistic",
        size: tuple[int, int] = (1024, 1024),
        model: str | None = None,
        request_id: str | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        if not prompt or not prompt.strip():
            raise ValidationError("A non-empty prompt is required", field="prompt")

        rid = request_id or f"img_{len(self._requests) + 1}"
        generator = self._resolve_generator(style)

        from modules.ai_video_studio.ai_image_generator.generators import get_generator

        result = get_generator(generator).generate(prompt=prompt, size=size, model=model, **params)
        record = {"id": rid, "style": style, "size": list(size), "result": result}
        self._requests[rid] = record
        return record

    def _resolve_generator(self, style: str) -> str:
        mapping = {
            "realistic": "realistic",
            "anime": "anime",
            "cinematic": "cinematic",
            "fantasy": "fantasy",
            "architecture": "architecture",
            "agriculture": "agriculture",
            "medical": "medical",
            "ecommerce": "ecommerce",
            "product": "product",
            "logo": "logo",
            "banner": "banner",
            "thumbnail": "thumbnail",
            "icon": "icon",
            "infographic": "infographic",
        }
        if style not in mapping:
            raise ValidationError(f"Unknown style '{style}'", field="style")
        return mapping[style]

    def status(self, request_id: str) -> dict[str, Any] | None:
        record = self._requests.get(request_id)
        return dict(record) if record else None

    def list_requests(self) -> list[str]:
        return list(self._requests.keys())


_image_engine: ImageEngine | None = None


def get_image_engine() -> ImageEngine:
    global _image_engine
    if _image_engine is None:
        _image_engine = ImageEngine()
    return _image_engine
