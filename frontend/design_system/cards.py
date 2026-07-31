from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CardSpec:
    """Definition of a card component."""

    title: str = ""
    subtitle: str = ""
    content: str = ""
    footer: str = ""
    variant: str = "default"  # default | outlined | elevated | interactive
    actions: list[dict[str, Any]] = field(default_factory=list)


class Cards:
    """Builds card definitions."""

    VARIANTS = ("default", "outlined", "elevated", "interactive")

    def __init__(self) -> None:
        self._cards: dict[str, CardSpec] = {}

    def register(self, name: str, spec: CardSpec) -> None:
        if spec.variant not in self.VARIANTS:
            raise ValueError(f"invalid card variant: {spec.variant}")
        self._cards[name] = spec

    def get(self, name: str) -> CardSpec:
        if name not in self._cards:
            raise KeyError(f"unknown card: {name}")
        return self._cards[name]

    def build(self, name: str, **props: Any) -> dict[str, Any]:
        return {"type": "card", "name": name, **vars(self.get(name)), "props": props}

    def metric(self, label: str, value: str, delta: str | None = None, **props: Any) -> dict[str, Any]:
        spec = CardSpec(
            title=label,
            content=value,
            footer=delta or "",
            variant="elevated",
        )
        return self.build(spec.title, **{"__spec": spec, **props}) if False else {
            "type": "metric_card",
            "label": label,
            "value": value,
            "delta": delta,
            "props": props,
        }
