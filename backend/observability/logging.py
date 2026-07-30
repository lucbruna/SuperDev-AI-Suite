"""Structured logging configuration using structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

try:
    import structlog
    from structlog.contextvars import bind_contextvars, merge_contextvars, reset_contextvars

    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


def setup_logging(level: str = "INFO", json_output: bool = True) -> None:
    """Configure structured logging with structlog.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_output: If True, output JSON. If False, use colorful console output.
    """
    if not HAS_STRUCTLOG:
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
        )
        return

    processors: list[Any] = [
        merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to pass through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: str | None = None) -> Any:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically module name).

    Returns:
        A structlog BoundLogger or stdlib Logger.
    """
    if HAS_STRUCTLOG:
        return structlog.get_logger(name)
    return logging.getLogger(name or "superdev")


def bind_request_context(request_id: str, user_id: str | None = None, org_id: str | None = None) -> None:
    """Bind request-scoped context variables to all log entries."""
    if HAS_STRUCTLOG:
        ctx: dict[str, str] = {"request_id": request_id}
        if user_id:
            ctx["user_id"] = user_id
        if org_id:
            ctx["org_id"] = org_id
        bind_contextvars(**ctx)


def reset_request_context() -> None:
    """Reset all request-scoped context variables."""
    if HAS_STRUCTLOG:
        reset_contextvars()
