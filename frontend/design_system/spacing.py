from __future__ import annotations

from typing import Any


class Spacing:
    """Spacing scale based on a base unit."""

    BASE = 4

    def __init__(self) -> None:
        self._tokens: dict[str, int] = {
            "none": 0,
            "xs": self.BASE,        # 4
            "sm": self.BASE * 2,    # 8
            "md": self.BASE * 4,    # 16
            "lg": self.BASE * 6,    # 24
            "xl": self.BASE * 8,    # 32
            "2xl": self.BASE * 12,  # 48
            "3xl": self.BASE * 16,  # 64
        }
        self._radii: dict[str, int] = {
            "none": 0,
            "sm": 4,
            "md": 8,
            "lg": 12,
            "full": 9999,
        }

    def get_spacing(self) -> dict[str, int]:
        return dict(self._tokens)

    def space(self, token: str) -> int:
        if token not in self._tokens:
            raise KeyError(f"unknown spacing token: {token}")
        return self._tokens[token]

    def radius(self, token: str) -> int:
        if token not in self._radii:
            raise KeyError(f"unknown radius token: {token}")
        return self._radii[token]

    def get_tokens(self) -> dict[str, Any]:
        return {"spacing": dict(self._tokens), "radii": dict(self._radii)}
