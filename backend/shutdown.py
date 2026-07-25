from __future__ import annotations

import asyncio
import logging

from backend.registry import service_registry

logger = logging.getLogger("superdev")


async def shutdown_handler() -> None:
    logger.info("Running shutdown cleanup")

    redis_client = service_registry.get("redis")
    if redis_client is not None:
        try:
            await redis_client.aclose()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning("Error closing Redis connection", extra={"error": str(e)})

    db_engine = service_registry.get("db_engine")
    if db_engine is not None:
        try:
            await db_engine.dispose()
            logger.info("Database engine disposed")
        except Exception as e:
            logger.warning("Error disposing database engine", extra={"error": str(e)})

    http_client = service_registry.get("http_client")
    if http_client is not None:
        try:
            await http_client.aclose()
            logger.info("HTTP client closed")
        except Exception as e:
            logger.warning("Error closing HTTP client", extra={"error": str(e)})

    providers = service_registry.get_all("providers") or {}
    for provider_name, provider_client in providers.items():
        if hasattr(provider_client, "aclose"):
            try:
                await provider_client.aclose()
                logger.info("Provider client closed", extra={"provider": provider_name})
            except Exception as e:
                logger.warning("Error closing provider", extra={"provider": provider_name, "error": str(e)})

    pending_tasks = service_registry.get("background_tasks", [])
    for task in pending_tasks:
        if not task.done():
            task.cancel()
    if pending_tasks:
        await asyncio.gather(*pending_tasks, return_exceptions=True)
        logger.info("Background tasks cancelled", extra={"count": len(pending_tasks)})

    service_registry.clear()
    logger.info("Shutdown cleanup complete")