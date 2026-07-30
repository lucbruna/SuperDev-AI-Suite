from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    id: str
    data: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
