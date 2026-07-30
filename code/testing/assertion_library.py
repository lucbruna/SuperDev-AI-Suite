from __future__ import annotations

import logging
from typing import Any


class AssertionLibrary:
    """Provides assertion helpers for tests."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.assertions")

    def assert_equal(self, actual: Any, expected: Any, msg: str = "") -> None:
        if actual != expected:
            raise AssertionError(msg or f"Expected {expected!r}, got {actual!r}")

    def assert_true(self, value: Any, msg: str = "") -> None:
        if not value:
            raise AssertionError(msg or f"Expected truthy value, got {value!r}")

    def assert_raises(self, exception_class: type, func: Any, *args: Any, **kwargs: Any) -> None:
        try:
            func(*args, **kwargs)
        except exception_class:
            return
        raise AssertionError(f"Expected {exception_class.__name__} was not raised")
