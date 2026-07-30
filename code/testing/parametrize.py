from __future__ import annotations

import logging
from typing import Any


class Parametrize:
    """Provides parametrized test support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.parametrize")

    def parametrize(self, argnames: str, argvalues: list[Any]) -> list[dict[str, Any]]:
        names = [n.strip() for n in argnames.split(",")]
        cases: list[dict[str, Any]] = []
        for vals in argvalues:
            case = dict(zip(names, vals if isinstance(vals, (list, tuple)) else [vals]))
            cases.append(case)
        self._log.info("Generated %d parametrized cases", len(cases))
        return cases
