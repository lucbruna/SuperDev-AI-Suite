"""Base classes for data processing."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProcessingError(Exception):
    """Raised when a processor fails."""


class Processor(ABC):
    """Transforms a single record dict into an enriched one."""

    name = "base"

    @abstractmethod
    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        """Returns a processed copy of the record."""
