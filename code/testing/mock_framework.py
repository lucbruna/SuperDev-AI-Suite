from __future__ import annotations

import logging
from typing import Any


class MockFramework:
    """Creates mock objects for testing."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.testing.mock")

    def mock(self, spec: type | None = None) -> Any:
        return _MockObject(spec)

    def spy(self, obj: Any, method: str) -> "_Spy":
        return _Spy(obj, method)


class _MockObject:
    def __init__(self, spec: type | None = None) -> None:
        self._spec = spec

    def __getattr__(self, name: str) -> Any:
        return _MockObject()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return None


class _Spy:
    def __init__(self, obj: Any, method: str) -> None:
        self._obj = obj
        self._method = method
        self.calls: list[tuple[tuple, dict]] = []

    def __enter__(self) -> "_Spy":
        return self

    def __exit__(self, *args: Any) -> None:
        pass
