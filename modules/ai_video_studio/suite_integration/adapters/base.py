"""Suite adapter base — contract + import helpers for platform components.

The AI Video Studio is a native module of the SuperDev suite: it lives at
``<suite_root>/SuperDev/modules/ai_video_studio``. Platform packages
(``SuperDev.integration``, ``SuperDev.security``, ``SuperDev.monitoring``,
``SuperDev.workflow``) become importable once the directory containing the
``SuperDev`` package is on ``sys.path``. ``ensure_suite_importable`` does
that lazily, so adapters work no matter the process working directory.

Every adapter implements the same contract: ``name``, ``description``,
``platform_module`` (the suite module it bridges to), ``actions`` and a
``status()`` report. Action methods must fail softly — never raise — and
report a ``platform`` flag so callers know whether the suite component (or
the local fallback) answered.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

# <suite_root>/SuperDev/modules/ai_video_studio/suite_integration/adapters/base.py
# parents[3] == <...>/modules, parents[4] == <...>/SuperDev (suite repo root)
_SUITE_ROOT = Path(__file__).resolve().parents[4]
# The directory that must be on sys.path for ``import SuperDev`` to resolve.
_SUITE_IMPORT_ROOT = _SUITE_ROOT.parent


def ensure_suite_importable() -> None:
    """Make the SuperDev suite root importable (idempotent, safe).

    Only when the suite root directory is literally named ``SuperDev`` (the
    canonical layout); otherwise the adapters degrade to local fallbacks.
    """
    if _SUITE_ROOT.name != "SuperDev":
        return
    root = str(_SUITE_IMPORT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def has_module(name: str) -> bool:
    """True when *name* is importable (never raises)."""
    ensure_suite_importable()
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def import_optional(name: str) -> Any | None:
    """Import *name*, returning None instead of raising on any failure."""
    if not has_module(name):
        return None
    try:
        return importlib.import_module(name)
    except Exception:  # noqa: BLE001 — optional platform components
        return None


class SuiteAdapter:
    """Base for every platform adapter (reuse-or-fallback contract)."""

    name: str = "adapter"
    description: str = ""
    platform_module: str = ""
    actions: tuple[str, ...] = ()

    def __init__(self) -> None:
        self._error: str | None = None

    def available(self) -> bool:
        """True when the platform module actually imports (not just exists)."""
        if not self.platform_module:
            return False
        return import_optional(self.platform_module) is not None

    def status(self) -> dict[str, Any]:
        """Adapter status: availability, bridged module and last error."""
        return {
            "name": self.name,
            "description": self.description,
            "platform_module": self.platform_module,
            "available": self.available(),
            "actions": list(self.actions),
            "error": self._error,
        }

    def capabilities(self) -> dict[str, Any]:
        """What the adapter exposes to the platform / to callers."""
        return {
            "adapter": self.name,
            "description": self.description,
            "actions": list(self.actions),
        }
