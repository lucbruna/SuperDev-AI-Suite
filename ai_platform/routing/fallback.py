from __future__ import annotations
import asyncio
import logging
from typing import Any, Callable, Awaitable, Optional

from ..providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class FallbackHandler:
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def execute_with_fallback(
        self,
        primary_provider: BaseProvider,
        fallback_providers: list[BaseProvider],
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await func(primary_provider, *args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Primary provider failed (attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        for fallback in fallback_providers:
            try:
                logger.info(f"Trying fallback provider: {getattr(fallback.config, 'name', 'unknown')}")
                return await func(fallback, *args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Fallback provider failed: {e}")
                continue

        raise RuntimeError(f"All providers failed. Last error: {last_error}")
