"""Graceful signal handlers for SIGTERM/SIGINT."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys

logger = logging.getLogger("superdev")

# Module-level flag checked during shutdown
_shutdown_requested = False
_shutdown_timeout = 30.0


def _request_shutdown(signum: int, frame: Any) -> None:
    """Handle SIGTERM/SIGINT by setting flag and logging."""
    global _shutdown_requested
    sig_name = signal.Signals(signum).name
    logger.info("Received %s — initiating graceful shutdown", sig_name)
    _shutdown_requested = True


def is_shutdown_requested() -> bool:
    """Check if a shutdown signal has been received."""
    return _shutdown_requested


def register_signal_handlers(timeout: float = 30.0) -> None:
    """Register SIGTERM and SIGINT handlers for graceful shutdown.

    Args:
        timeout: Maximum seconds to wait for shutdown before force exit.
    """
    global _shutdown_timeout
    _shutdown_timeout = timeout

    if sys.platform != "win32":
        # Unix: SIGTERM + SIGINT + SIGHUP
        signal.signal(signal.SIGTERM, _request_shutdown)
        signal.signal(signal.SIGINT, _request_shutdown)
        try:
            signal.signal(signal.SIGHUP, _request_shutdown)
        except (OSError, ValueError):
            pass  # SIGHUP not available on some platforms
    else:
        # Windows: only SIGINT (Ctrl+C) and SIGBREAK (Ctrl+Break)
        signal.signal(signal.SIGINT, _request_shutdown)
        try:
            signal.signal(signal.SIGBREAK, _request_shutdown)  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

    logger.info(
        "Signal handlers registered (SIGTERM/SIGINT → graceful shutdown, timeout=%ds)",
        int(timeout),
    )


def force_exit_if_needed() -> None:
    """Force exit if shutdown is taking too long. Call from a watchdog."""
    if _shutdown_requested:
        logger.warning("Forcing exit after timeout")
        os._exit(1)  # noqa: SLF001 — intentional force exit
