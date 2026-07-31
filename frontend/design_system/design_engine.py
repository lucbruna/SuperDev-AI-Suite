from __future__ import annotations

import logging
from typing import Any

from .buttons import Buttons
from .cards import Cards
from .colors import ColorPalette
from .dialogs import Dialogs
from .forms import Forms
from .navigation import Navigation
from .notifications import Notifications
from .spacing import Spacing
from .tables import Tables
from .typography import Typography


class DesignEngine:
    """Central coordinator for the design system."""

    def __init__(self, mode: str = "light") -> None:
        self._log = logging.getLogger("superdev.frontend.design")
        self.colors = ColorPalette(mode)
        self.typography = Typography()
        self.spacing = Spacing()
        self.buttons = Buttons(self.colors)
        self.forms = Forms()
        self.tables = Tables()
        self.dialogs = Dialogs()
        self.cards = Cards()
        self.navigation = Navigation()
        self.notifications = Notifications()
        self.buttons.default_variants()

    @property
    def mode(self) -> str:
        return self.colors.mode

    def set_mode(self, mode: str) -> None:
        self.colors.set_mode(mode)

    def toggle_mode(self) -> str:
        new_mode = "dark" if self.colors.mode == "light" else "light"
        self.colors.set_mode(new_mode)
        self.buttons.default_variants()
        return new_mode

    def tokens(self) -> dict[str, Any]:
        return {
            "mode": self.colors.mode,
            "colors": self.colors.get_colors(),
            "typography": self.typography.get_typography(),
            "spacing": self.spacing.get_tokens(),
            "button_variants": self.buttons.list(),
        }

    def seed_defaults(self) -> None:
        self.navigation.register("default", self.navigation.default_structure())
        self.forms.register_template(
            "login",
            [
                self.forms.field("email", "Email", "email", required=True),
                self.forms.field("password", "Password", "password", required=True),
            ],
        )
        self.forms.register_template(
            "profile",
            [
                self.forms.field("name", "Name", "text", required=True),
                self.forms.field("email", "Email", "email", required=True),
            ],
        )
        self.tables.register_template(
            "agents",
            [
                self.tables.column("name", "Name", sortable=True),
                self.tables.column("status", "Status"),
                self.tables.column("model", "Model"),
            ],
        )
        self.tables.register_template(
            "projects",
            [
                self.tables.column("name", "Name", sortable=True),
                self.tables.column("status", "Status"),
                self.tables.column("updated_at", "Updated"),
            ],
        )
