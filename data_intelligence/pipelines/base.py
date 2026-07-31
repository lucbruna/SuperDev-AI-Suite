"""Base classes for data pipeline stages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PipelineError(Exception):
    """Raised when a pipeline stage fails."""


class PipelineStage(ABC):
    """A single step in a data pipeline.

    ``run`` receives the current records plus a shared mutable context dict
    and returns ``(records, context)``.
    """

    stage_type = "base"

    def __init__(self, **config: Any) -> None:
        self.config = config

    @abstractmethod
    def run(self, records: list[dict[str, Any]],
            context: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                              dict[str, Any]]:
        """Processes the records and returns the updated records."""
