from __future__ import annotations

from typing import Any


class ReleaseManager:
    """Manages software releases and promotions."""

    def __init__(self) -> None:
        self._releases: dict[str, dict[str, Any]] = {}
        self._promotions: list[dict[str, Any]] = []

    def create_release(self, version: str, artifacts: list[str]) -> str:
        self._releases[version] = {"version": version, "artifacts": artifacts}
        return version

    def get_release(self, version: str) -> dict[str, Any] | None:
        return self._releases.get(version)

    @property
    def release_count(self) -> int:
        return len(self._releases)

    def promote(self, version: str, environment: str) -> bool:
        if version in self._releases:
            self._promotions.append({"version": version, "environment": environment})
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "releases": list(self._releases.values()),
            "promotions": self._promotions,
            "release_count": self.release_count,
        }
