from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FrontendContext:
    """Shared context passed across frontend subsystems."""

    user: dict[str, Any] | None = None
    theme: str = "light"
    language: str = "pt_BR"
    active_route: str = "/"
    screen_size: dict[str, int] = field(default_factory=lambda: {"width": 1440, "height": 900})
    platform: str = "web"
    state: dict[str, Any] = field(default_factory=dict)
