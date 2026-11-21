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
    """Expose this checkout under the canonical ``SuperDev`` package name.

    The repository is itself the SuperDev package, but CI and developer
    checkouts are commonly named ``SuperDev-AI-Suite`` rather than
    ``SuperDev``. In that layout, load the repository root as the package
    when no canonical package is already importable.
    """
    if _SUITE_ROOT.name == "SuperDev":
        root = str(_SUITE_IMPORT_ROOT)
        if root not in sys.path:
            sys.path.insert(0, root)
        return

    if not (_SUITE_ROOT / "__init__.py").is_file():
        return

    # A different installed distribution (or a namespace package) can make
    # find_spec("SuperDev") succeed without exposing this checkout's modules.
    # Prefer an already-loaded package, but extend its search path to this repo.
    existing = sys.modules.get("SuperDev")
    if existing is None:
        try:
            existing = importlib.import_module("SuperDev")
        except (ImportError, ModuleNotFoundError):
            existing = None
    existing_path = getattr(existing, "__path__", None)
    if existing_path is not None:
        root = str(_SUITE_ROOT)
        if root not in existing_path:
            existing_path.append(root)
        return

    spec = importlib.util.spec_from_file_location(
        "SuperDev",
        _SUITE_ROOT / "__init__.py",
        submodule_search_locations=[str(_SUITE_ROOT)],
    )
    if spec is None or spec.loader is None:
        return
    package = importlib.util.module_from_spec(spec)
    sys.modules["SuperDev"] = package
    try:
        spec.loader.exec_module(package)
    except Exception:
        sys.modules.pop("SuperDev", None)
        raise


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
