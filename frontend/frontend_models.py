from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScreenModel:
    """Model describing a frontend screen."""

    name: str
    route: str
    title: str
    layout: str = "default"
    requires_auth: bool = True
    permissions: list[str] = field(default_factory=list)
    props: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentModel:
    """Model describing a reusable UI component."""

    name: str
    tag: str
    props_schema: dict[str, Any] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    styles: dict[str, Any] = field(default_factory=dict)
