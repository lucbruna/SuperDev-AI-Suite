from __future__ import annotations

from typing import Any, Callable


class InterceptorChain:
    """Chain of interceptors applied around a gRPC call.

    Interceptors are functions of the form ``async def interceptor(next_func, ctx)``
    that may perform work before and after delegating to ``next_func(ctx)``.
    """

    def __init__(self) -> None:
        self.interceptors: list[Callable] = []

    def add(self, interceptor: Callable) -> None:
        self.interceptors.append(interceptor)

    def __len__(self) -> int:
        return len(self.interceptors)

    async def execute(self, handler: Callable, ctx: Any) -> Any:
        async def run(index: int = 0) -> Any:
            if index < len(self.interceptors):
                interceptor = self.interceptors[index]
                return await interceptor(lambda c: run(index + 1), c if (c := ctx) else ctx)
            result = handler(ctx)
            if hasattr(result, "__await__"):
                return await result
            return result

        return await run()

    def to_dict(self) -> dict:
        return {"interceptors": len(self.interceptors)}
