"""Java package — JDK toolchain facade (Vol 12, Fase 19)."""
from __future__ import annotations

from modules.aios.java.gradle import GradleManager, GradleUnavailableError
from modules.aios.java.java_client import (
    JavaClient,
    JavaUnavailableError,
    require_java_action,
)
from modules.aios.java.java_runtime import JavaRuntime, get_java_runtime
from modules.aios.java.maven import MavenManager, MavenUnavailableError

__all__ = [
    "GradleManager",
    "GradleUnavailableError",
    "JavaClient",
    "JavaRuntime",
    "JavaUnavailableError",
    "get_java_runtime",
    "MavenManager",
    "MavenUnavailableError",
    "require_java_action",
]
