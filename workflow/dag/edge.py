from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Edge:
    source: str
    target: str
    weight: float = 1.0
