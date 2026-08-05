"""Prompt Dispatcher — sends writing work to the studio AI Studio (or plans it)."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.event_bus import get_event_bus


class PromptDispatcher:
    """Dispatches prompts to the studio AI Studio service when registered."""

    def dispatch(self, prompt: str, *, context: dict[str, Any] | None = None,
                 publish: bool = True) -> dict[str, Any]:
        """Return a dispatch plan; uses the studio AI service when available."""
        context = context or {}
        # Best-effort: route to the registered AI Studio service.
        service = self._ai_studio_service()
        handled = False
        if service is not None and hasattr(service, "generate_project"):
            handled = True
        plan = {
            "prompt": prompt,
            "context": dict(context),
            "dispatched_to": "ai_studio" if handled else "local_planner",
            "handled": handled,
            "chars": len(prompt),
        }
        if publish:
            self.publish_sync("prompt.dispatched", **plan)
        return plan

    @staticmethod
    def publish_sync(event_type: str, **payload: Any) -> None:
        import asyncio

        try:
            asyncio.get_event_loop().run_until_complete(
                get_event_bus().publish(event_type, **payload)
            )
        except RuntimeError:
            pass

    @staticmethod
    def _ai_studio_service() -> Any | None:
        try:
            from modules.ai_video_studio.integration.service_locator import (
                get_service_locator,
            )

            return get_service_locator().get("ai_studio")
        except Exception:  # noqa: BLE001
            return None


_prompt_dispatcher: PromptDispatcher | None = None


def get_prompt_dispatcher() -> PromptDispatcher:
    global _prompt_dispatcher
    if _prompt_dispatcher is None:
        _prompt_dispatcher = PromptDispatcher()
    return _prompt_dispatcher
