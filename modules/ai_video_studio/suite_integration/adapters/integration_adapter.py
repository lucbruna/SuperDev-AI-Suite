"""Integration adapter — register the studio with the suite Integration & API Engine.

Bridges to ``SuperDev.integration``: installs an ``IntegrationDefinition``
for the AI Video Studio into the suite engine's registry and reports the
engine status. This is the concrete "the studio is a native module of the
suite" step.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
    import_optional,
)
from modules.ai_video_studio.suite_integration.suite_manifest import SUITE_MANIFEST

STUDIO_INTEGRATION_ID = "ai_video_studio"


class IntegrationAdapter(SuiteAdapter):
    """Registers the studio as a first-class suite integration."""

    name = "integration"
    description = "Register the AI Video Studio in the suite Integration & API Engine"
    platform_module = "SuperDev.integration"
    actions = ("install_integration", "engine_status")

    def __init__(self) -> None:
        super().__init__()
        #: Single engine instance shared by registration and status calls.
        self._engine: Any = None
        self._installed = False

    def _get_engine(self) -> Any | None:
        """Return the shared suite engine, initialized exactly once."""
        ensure_suite_importable()
        if self._engine is not None:
            return self._engine
        engine_mod = import_optional("SuperDev.integration.integration_engine")
        if engine_mod is None:
            return None
        try:
            self._engine = engine_mod.IntegrationEngine().initialize()
        except Exception as e:  # noqa: BLE001
            self._error = f"engine init failed: {e}"
            self._engine = None
        return self._engine

    def register_with_platform(self) -> dict[str, Any]:
        """Install the studio's integration definition into the suite engine."""
        engine = self._get_engine()
        if engine is None:
            self._error = self._error or "suite integration engine unavailable"
            return {"registered": False, "error": self._error, "platform": False}
        try:
            from SuperDev.integration.integration_models import IntegrationDefinition

            payload: dict[str, Any] = {"platform": True}
            if not self._installed:
                definition = IntegrationDefinition(
                    integration_id=STUDIO_INTEGRATION_ID,
                    name="AI Video Studio",
                    category="media",
                    provider="superdev",
                    version=SUITE_MANIFEST.version,
                    description=(
                        "AI Video Studio — video/image/voice/music generation, "
                        "digital avatars, lip-sync, editing, effects and export"
                    ),
                    metadata={"package": "modules.ai_video_studio"},
                )
                result = engine.install_integration(definition)
                data = getattr(result, "data", None)
                if isinstance(data, dict):
                    payload["result"] = data
                self._installed = bool(getattr(result, "success", True))
            payload["registered"] = self._installed
            payload["integration_id"] = STUDIO_INTEGRATION_ID
            payload["engine_status"] = engine.status()
            return payload
        except Exception as e:  # noqa: BLE001 — registration is best-effort
            self._error = f"registration failed: {e}"
            return {"registered": False, "error": self._error, "platform": True}

    def engine_status(self) -> dict[str, Any]:
        """Status of the shared suite integration engine (best-effort)."""
        engine = self._get_engine()
        if engine is None:
            return {"started": False, "platform": False, "error": self._error}
        try:
            return {**engine.status(), "platform": True}
        except Exception as e:  # noqa: BLE001
            self._error = f"engine status failed: {e}"
            return {"started": False, "error": self._error, "platform": True}
