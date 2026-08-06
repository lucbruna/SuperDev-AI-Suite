"""Small deterministic text helpers."""
from __future__ import annotations

import re

__all__ = ["indent", "slugify", "truncate"]

_NON_ALNUM = re.compile(r"[\W_]+")


def slugify(text: str) -> str:
    """Lowercase, non-alphanumeric runs become dashes, dashes stripped."""
    return _NON_ALNUM.sub("-", text.strip().lower()).strip("-")


def truncate(text: str, max_length: int = 120, suffix: str = "...") -> str:
    """Cut ``text`` to ``max_length`` appending ``suffix`` when truncated."""
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return text[:max_length]
    return text[: max_length - len(suffix)] + suffix


def indent(text: str, spaces: int = 4) -> str:
    """Prefix every line with ``spaces`` spaces."""
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())
