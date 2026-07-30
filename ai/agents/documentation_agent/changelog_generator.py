from __future__ import annotations

from typing import Any


class ChangelogGenerator:
    """Generates changelogs from version entries."""

    def __init__(self) -> None:
        self._entries: dict[str, dict[str, Any]] = {}

    def add_entry(self, version: str, date: str, changes: list[str]) -> str:
        self._entries[version] = {"version": version, "date": date, "changes": changes}
        return version

    def get_entry(self, version: str) -> dict[str, Any] | None:
        return self._entries.get(version)

    def remove_entry(self, version: str) -> bool:
        if version in self._entries:
            del self._entries[version]
            return True
        return False

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def generate_changelog(self) -> str:
        lines: list[str] = ["# Changelog", ""]
        for ver, entry in sorted(self._entries.items(), reverse=True):
            lines.append(f"## [{ver}] - {entry['date']}")
            for change in entry["changes"]:
                lines.append(f"- {change}")
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": list(self._entries.values()),
            "entry_count": self.entry_count,
        }
