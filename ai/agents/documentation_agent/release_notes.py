from __future__ import annotations

from typing import Any


class ReleaseNotes:
    """Generates release notes for software releases."""

    def __init__(self) -> None:
        self._releases: dict[str, dict[str, Any]] = {}

    def add_release(self, version: str, notes: dict[str, Any]) -> str:
        self._releases[version] = {"version": version, "notes": notes}
        return version

    def get_release(self, version: str) -> dict[str, Any] | None:
        return self._releases.get(version)

    @property
    def release_count(self) -> int:
        return len(self._releases)

    def generate(self) -> str:
        lines: list[str] = ["# Release Notes", ""]
        for ver, rel in sorted(self._releases.items(), reverse=True):
            lines.append(f"## Version {ver}")
            for k, v in rel["notes"].items():
                if isinstance(v, list):
                    lines.append(f"### {k.capitalize()}")
                    for item in v:
                        lines.append(f"- {item}")
                else:
                    lines.append(f"- **{k}**: {v}")
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "releases": list(self._releases.values()),
            "release_count": self.release_count,
        }
