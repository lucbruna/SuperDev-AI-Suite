from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

from ..monitoring_models import SpanStatus

from .tracer import Tracer

F = TypeVar("F", bound=Callable[..., Any])


class Instrumentation:
    """Auto-instrumentation for functions and async calls."""

    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def instrument(
        self,
        name: str = "",
        tags: dict[str, str] | None = None,
    ) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            operation = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self._tracer.in_span(operation, tags=tags):
                    return func(*args, **kwargs)

            return wrapper  # type: ignore[return-value]

        return decorator

    def instrument_async(
        self,
        name: str = "",
        tags: dict[str, str] | None = None,
    ) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            operation = name or func.__name__

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self._tracer.in_span(operation, tags=tags):
                    return await func(*args, **kwargs)

            return wrapper  # type: ignore[return-value]

        return decorator

    def instrument_method(
        self,
        cls: type,
        method_name: str,
        operation_name: str = "",
        tags: dict[str, str] | None = None,
    ) -> None:
        original = getattr(cls, method_name)
        operation = operation_name or f"{cls.__name__}.{method_name}"

        @functools.wraps(original)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            with self._tracer.in_span(operation, tags=tags):
                return original(self, *args, **kwargs)

        setattr(cls, method_name, wrapper)
