"""Go package — Go toolchain facade (Vol 12, Fase 20)."""
from __future__ import annotations

from modules.aios.go.build import GoBuild
from modules.aios.go.go_client import (
    GoClient,
    GoUnavailableError,
    require_go_action,
)
from modules.aios.go.go_runtime import GoRuntime, get_go_runtime
from modules.aios.go.modules import GoModules
from modules.aios.go.test import GoTest

__all__ = [
    "GoBuild",
    "GoClient",
    "GoModules",
    "GoRuntime",
    "GoTest",
    "GoUnavailableError",
    "get_go_runtime",
    "require_go_action",
]
