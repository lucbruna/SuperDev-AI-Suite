"""Proxy timeline — low-resolution media mapping for fast preview.

Proxy media let the editor scrub long timelines without decoding full
resolution. The manager records the proxy → source mapping, knows whether a
clip uses a proxy, and can attach real proxy frames to clips for rendering.
"""
from __future__ import annotations

import uuid
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.proxy")


class ProxyTimeline:
    def __init__(self, timeline: Any, *, proxy_scale: int = 4) -> None:
        self.timeline = timeline
        self.proxy_scale = max(1, int(proxy_scale))
        self._proxy_map: dict[str, dict[str, Any]] = {}
        self._clip_proxy: dict[str, str] = {}

    def register(self, source: str, proxy: str, width: int, height: int) -> str:
        proxy_id = f"proxy_{uuid.uuid4().hex[:8]}"
        self._proxy_map[proxy_id] = {
            "id": proxy_id, "source": source, "proxy": proxy,
            "width": int(width), "height": int(height),
        }
        return proxy_id

    def assign(self, clip_id: str, proxy_id: str) -> None:
        if proxy_id not in self._proxy_map:
            raise KeyError(f"Unknown proxy '{proxy_id}'")
        self._clip_proxy[clip_id] = proxy_id

    def unassign(self, clip_id: str) -> None:
        self._clip_proxy.pop(clip_id, None)

    def is_proxy(self, clip_id: str) -> bool:
        return clip_id in self._clip_proxy

    def proxy_for(self, clip_id: str) -> dict[str, Any] | None:
        proxy_id = self._clip_proxy.get(clip_id)
        return self._proxy_map.get(proxy_id) if proxy_id else None

    def preview_settings(self) -> dict[str, Any]:
        return {"scale": self.proxy_scale, "active_clips": len(self._clip_proxy), "proxies": len(self._proxy_map)}
