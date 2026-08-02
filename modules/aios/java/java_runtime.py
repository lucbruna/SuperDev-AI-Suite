"""Java runtime — facade over the JDK toolchain (Vol 12, Fase 19)."""
from __future__ import annotations

from typing import Any

from modules.aios.java.gradle import GradleManager, GradleUnavailableError
from modules.aios.java.java_client import JavaClient
from modules.aios.java.maven import MavenManager, MavenUnavailableError


class JavaRuntime:
    """Facade over javac/java plus gradle/maven.

    Stateless: managers are CLI wrappers. ``close`` is a no-op. Tools that
    are not installed (gradle, maven) degrade gracefully via *UnavailableError.
    """

    def __init__(self) -> None:
        self.client = JavaClient()
        self.gradle = GradleManager()
        self.maven = MavenManager()

    async def available(self) -> bool:
        return await self.client.ping()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort tool inventory; each tool degrades to None on error."""
        java_version = None
        gradle_version: str | None = None
        maven_version: str | None = None
        try:
            java_version = (await self.client.version())["version"]
        except (RuntimeError, Exception):  # noqa: BLE001
            java_version = None
        try:
            gradle_version = (await self.gradle.version())["version"]
        except GradleUnavailableError:
            gradle_version = None
        try:
            maven_version = (await self.maven.version())["version"]
        except MavenUnavailableError:
            maven_version = None
        return {
            "java": java_version,
            "gradle": gradle_version,
            "maven": maven_version,
        }

    async def close(self) -> None:
        """No-op — the java runtime is stateless."""


_java_runtime: JavaRuntime | None = None


def get_java_runtime() -> JavaRuntime:
    global _java_runtime
    if _java_runtime is None:
        _java_runtime = JavaRuntime()
    return _java_runtime


__all__ = ["JavaRuntime", "get_java_runtime"]
