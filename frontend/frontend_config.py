from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FrontendConfig:
    """Configuration for the frontend platform."""

    app_name: str = "SuperDev AI Suite"
    default_theme: str = "light"
    default_language: str = "pt_BR"
    base_url: str = "/"
    api_base: str = "/api"
    enable_realtime: bool = True
    enable_collaboration: bool = True
    routes: dict[str, dict[str, Any]] = field(default_factory=dict)
    plugins: list[str] = field(default_factory=list)
