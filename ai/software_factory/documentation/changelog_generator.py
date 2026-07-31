"""Generator for changelog files."""
from typing import List
from datetime import datetime
from .models import ChangelogEntry


class ChangelogGenerator:
    """Generates changelog documents."""

    def __init__(self):
        self._entries: List[ChangelogEntry] = []

    def add_entry(self, entry: ChangelogEntry) -> None:
        self._entries.append(entry)

    def generate(self, entries: List[ChangelogEntry] = None) -> str:
        if entries:
            self._entries = entries

        lines = ["# Changelog\n", "All notable changes to this project will be documented in this file.\n"]
        for entry in sorted(self._entries, key=lambda e: e.date, reverse=True):
            date_str = entry.date.strftime("%Y-%m-%d")
            lines.append(f"## [{entry.version}] - {date_str}\n")
            if entry.changes:
                lines.append("### Added")
                for change in entry.changes:
                    lines.append(f"- {change}")
                lines.append("")
            if entry.breaking:
                lines.append("### Changed (Breaking)")
                for breaking in entry.breaking:
                    lines.append(f"- {breaking}")
                lines.append("")
            if entry.deprecations:
                lines.append("### Deprecated")
                for dep in entry.deprecations:
                    lines.append(f"- {dep}")
                lines.append("")
        return "\n".join(lines)

    def get_entries(self) -> List[ChangelogEntry]:
        return list(self._entries)
