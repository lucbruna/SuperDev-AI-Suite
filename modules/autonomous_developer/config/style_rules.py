"""Style rules — formatting conventions for generated code.

Environment prefix: ``SUPERDEV_AD_STYLE_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class StyleRules:
    """Formatting conventions applied by the generator."""

    indent: int = 4
    max_line_length: int = 100
    quote_style: str = "double"  # double | single
    trailing_whitespace_forbidden: bool = True
    final_newline: bool = True
    import_order: str = "isort"  # isort | stdlib-first | none
    sort_imports: bool = True
    remove_unused_imports: bool = True
    name_conventions: dict[str, str] = field(default_factory=lambda: {
        "module": "snake_case",
        "class": "PascalCase",
        "function": "snake_case",
        "variable": "snake_case",
        "constant": "UPPER_SNAKE_CASE",
        "private": "leading underscore",
    })

    @classmethod
    def from_env(cls) -> StyleRules:
        cfg = cls()
        cfg.indent = int(os.getenv("SUPERDEV_AD_STYLE_INDENT", str(cfg.indent)))
        cfg.max_line_length = int(
            os.getenv("SUPERDEV_AD_STYLE_LINE_LENGTH", str(cfg.max_line_length))
        )
        cfg.quote_style = os.getenv("SUPERDEV_AD_STYLE_QUOTES", cfg.quote_style)
        cfg.sort_imports = _env_bool(
            "SUPERDEV_AD_STYLE_SORT_IMPORTS", cfg.sort_imports
        )
        return cfg
