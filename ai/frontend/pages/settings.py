"""
Settings Page
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SettingsSection:
    key: str
    label: str
    icon: str = ""
    settings: list = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = []


class SettingsPage:
    def __init__(self):
        self.sections: list = []
        self.active_section: str = "general"
        self.changes: dict[str, Any] = {}
        self.unsaved: bool = False

    def set_section(self, section: str) -> None:
        self.active_section = section

    def update_setting(self, key: str, value: Any) -> None:
        self.changes[key] = value
        self.unsaved = True

    def save(self) -> bool:
        self.changes.clear()
        self.unsaved = False
        return True

    def discard(self) -> None:
        self.changes.clear()
        self.unsaved = False

    def render(self) -> dict[str, Any]:
        return {"activeSection": self.active_section, "unsaved": self.unsaved, "changes": self.changes}
