"""Plugin adapter — expose the studio's capabilities as plugins.

Bridges to ``SuperDev.plugin_platform`` (the suite plugin platform). When
the platform is importable the studio's official plugin descriptors are
registered through it; when it is not (e.g. the top-level ``core`` package
it depends on is absent), a local descriptor registry keeps the studio's
plugin surface discoverable. Either way the adapter answers without raising.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
    import_optional,
)

#: Official studio plugins — (plugin_id, description).
STUDIO_PLUGINS: tuple[tuple[str, str], ...] = (
    ("ai_studio", "AI writing and direction (script, storyboard, plan)"),
    ("voice_studio", "Text-to-speech narration (edge-tts → gTTS → offline)"),
    ("avatar_engine", "Digital humans and virtual actor library"),
    ("speaking_avatar", "Narrated talking-avatar video with lip-sync"),
    ("lip_sync", "Viseme timelines from audio for the facial rig"),
    ("subtitle_studio", "SRT generation and subtitle translation"),
    ("export_service", "Multi-format export (mp4/webm/mov/gif)"),
    ("render_engine", "FFmpeg-backed rendering and muxing"),
)


class PluginAdapter(SuiteAdapter):
    """Studio plugin surface — suite platform with local registry fallback."""

    name = "plugins"
    description = "Expose the studio's official plugins via the suite plugin platform (local registry fallback)"
    platform_module = "SuperDev.plugin_platform"
    actions = ("register_plugins", "list_plugins")

    def __init__(self) -> None:
        super().__init__()
        self._registered: list[str] = []
        self._platform_registered = False

    def register_plugins(self) -> dict[str, Any]:
        """Register every official studio plugin (platform or local)."""
        ensure_suite_importable()
        platform = import_optional("SuperDev.plugin_platform")
        if platform is None:
            # Degraded mode: keep the surface discoverable locally.
            self._registered = [plugin_id for plugin_id, _ in STUDIO_PLUGINS]
            return {
                "platform": False,
                "registered": len(self._registered),
                "plugins": list(self._registered),
                "note": "suite plugin_platform unavailable; local descriptor registry used",
            }
        try:
            # Best-effort: any PluginManager-like API with register(name, plugin).
            manager_cls = getattr(platform, "PluginManager", None)
            manager = manager_cls() if manager_cls else None
            errors: list[str] = []
            for plugin_id, description in STUDIO_PLUGINS:
                plugin = {"id": plugin_id, "description": description, "provider": "ai_video_studio"}
                if manager is not None and hasattr(manager, "register"):
                    try:
                        manager.register(plugin_id, plugin)
                        self._registered.append(plugin_id)
                    except Exception as exc:  # noqa: BLE001 — per-plugin best effort
                        errors.append(f"{plugin_id}: {exc}")
                else:
                    self._registered.append(plugin_id)
            self._platform_registered = bool(self._registered)
            return {
                "platform": True,
                "registered": len(self._registered),
                "plugins": list(self._registered),
                "errors": errors,
            }
        except Exception as e:  # noqa: BLE001 — registration must not raise
            self._error = f"plugin registration failed: {e}"
            return {"platform": True, "registered": 0, "error": self._error}

    def list_plugins(self) -> dict[str, Any]:
        """Currently registered plugin ids + the studio plugin catalog."""
        return {
            "registered": list(self._registered),
            "catalog": [plugin_id for plugin_id, _ in STUDIO_PLUGINS],
            "platform": self._platform_registered,
        }
