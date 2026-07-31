"""
Settings Store
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SettingsState:
    theme: str = "dark"
    language: str = "pt"
    sidebar_collapsed: bool = False
    notifications_enabled: bool = True
    settings: dict[str, Any] = field(default_factory=dict)


class SettingsStore:
    def __init__(self):
        self.state = SettingsState()
        self.listeners: list = []

    def set_theme(self, theme: str) -> None:
        self.state.theme = theme
        self._notify()

    def set_language(self, language: str) -> None:
        self.state.language = language
        self._notify()

    def toggle_sidebar(self) -> None:
        self.state.sidebar_collapsed = not self.state.sidebar_collapsed
        self._notify()

    def update(self, settings: dict[str, Any]) -> None:
        self.state.settings.update(settings)
        self._notify()

    def _notify(self) -> None:
        for cb in self.listeners:
            cb(self.state)

    def on_change(self, callback) -> None:
        self.listeners.append(callback)

    def render(self) -> dict[str, Any]:
        return {"theme": self.state.theme, "language": self.state.language, "sidebarCollapsed": self.state.sidebar_collapsed}
