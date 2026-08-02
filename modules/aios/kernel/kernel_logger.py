"""Kernel logger — ring-buffer logging via the Vol 10 integration logger."""
from __future__ import annotations
from typing import Any


class KernelLogger:
    """Writes ``kernel.*`` entries through the integration logger."""

    def __init__(self) -> None:
        self._logger: Any | None = None

    def _get(self) -> Any:
        if self._logger is None:
            try:
                from modules.ai_video_studio.integration.integration_logger import (
                    get_integration_logger,
                )

                self._logger = get_integration_logger()
            except Exception:  # noqa: BLE001
                self._logger = None
        return self._logger

    def log(self, component: str, message: str, *, level: str = "info", payload: dict[str, Any] | None = None) -> None:
        logger = self._get()
        if logger is None:
            return
        try:
            logger.log(
                f"kernel.{component}", message, level=level, payload=payload
            )
        except Exception:  # noqa: BLE001
            pass

    def entries(self, limit: int = 100) -> list[dict[str, Any]]:
        logger = self._get()
        if logger is None:
            return []
        return [
            e
            for e in logger.entries(limit=limit)
            if str(e.get("service", "")).startswith("kernel.")
        ]


_kernel_logger: KernelLogger | None = None


def get_kernel_logger() -> KernelLogger:
    global _kernel_logger
    if _kernel_logger is None:
        _kernel_logger = KernelLogger()
    return _kernel_logger
