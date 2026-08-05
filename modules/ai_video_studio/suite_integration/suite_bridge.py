"""Suite bridge — the AI Video Studio ↔ SuperDev platform connection (Volume 10).

``SuiteBridge`` is the single entry point that makes the studio a native
module of the SuperDev suite:

* **Discover** — which platform services are importable right now
  (integration engine, JWT auth, SSRF guards, monitoring, workflows,
  plugin platform) via per-service adapters.
* **Reuse** — call the platform components instead of duplicating them
  (each adapter falls back to a local equivalent when the platform piece
  is missing, so the studio never breaks).
* **Register** — install the studio into the suite integration engine,
  register its pipelines as workflows and its official plugins.

All results are JSON-serializable and never raise.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.suite_integration.adapters import get_adapters
from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
    has_module,
)
from modules.ai_video_studio.suite_integration.suite_manifest import SUITE_MANIFEST


class SuiteBridge:
    """Orchestrates platform discovery, registration and reuse."""

    def __init__(self, adapters: list[SuiteAdapter] | None = None) -> None:
        self._adapters = {a.name: a for a in (adapters if adapters is not None else get_adapters())}
        self._registration: dict[str, Any] | None = None

    # ── discovery ────────────────────────────────────────────────
    def adapters(self) -> dict[str, dict[str, Any]]:
        """Per-adapter status report (availability + actions)."""
        return {name: adapter.status() for name, adapter in self._adapters.items()}

    def capabilities(self) -> dict[str, Any]:
        """What each adapter exposes to the platform."""
        return {name: adapter.capabilities() for name, adapter in self._adapters.items()}

    def manifest(self) -> dict[str, Any]:
        """The studio's declared platform contract."""
        return SUITE_MANIFEST.to_dict()

    def check(self) -> dict[str, Any]:
        """Full platform capability matrix for ops dashboards."""
        ensure_suite_importable()
        return {
            "module": SUITE_MANIFEST.module,
            "version": SUITE_MANIFEST.version,
            "native": has_module("SuperDev"),
            "platform_modules": {name: adapter.available() for name, adapter in self._adapters.items()},
            "adapters": self.adapters(),
            "registered": self._registration is not None,
        }

    # ── registration ─────────────────────────────────────────────
    def register_with_platform(self) -> dict[str, Any]:
        """Install the studio into the suite (idempotent, cached result)."""
        if self._registration is not None:
            return self._registration
        results: dict[str, Any] = {
            "integration": self._adapters["integration"].register_with_platform(),
            "workflow": self._adapters["workflow"].register_pipeline(),
            "plugins": self._adapters["plugins"].register_plugins(),
        }
        self._registration = results
        return results

    # ── convenience delegates (reuse) ────────────────────────────
    async def verify_token(self, token: str | None) -> dict[str, Any]:
        """Verify a bearer token via the platform JWT manager."""
        return await self._adapters["auth"].verify_token(token)

    def validate_url(self, url: str, *, allow_private: bool = False) -> dict[str, Any]:
        """Validate a URL against the suite SSRF policy."""
        return self._adapters["security"].validate_url(url, allow_private=allow_private)

    def record_metric(self, metric: str, value: int = 1, **labels: Any) -> dict[str, Any]:
        """Record a studio metric (local counters, suite-ready)."""
        return self._adapters["observability"].record(metric, value, **labels)


_bridge: SuiteBridge | None = None


def get_suite_bridge() -> SuiteBridge:
    """Return the shared suite bridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = SuiteBridge()
    return _bridge
