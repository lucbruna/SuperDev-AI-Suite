import asyncio
from collections.abc import Coroutine
from typing import Any


async def run_parallel(*tasks: Coroutine[Any, Any, Any]) -> list[Any]:
    return await asyncio.gather(*tasks)


async def run_with_timeout(
    coro: Coroutine[Any, Any, Any],
    timeout: float,
) -> Any:
    return await asyncio.wait_for(coro, timeout=timeout)


async def gather_with_concurrency(
    n: int,
    *tasks: Coroutine[Any, Any, Any],
) -> list[Any]:
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task: Coroutine[Any, Any, Any]) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(t) for t in tasks))
