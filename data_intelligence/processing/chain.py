"""Processing chain (composes processors in order)."""

from __future__ import annotations

from typing import Any

from data_intelligence.processing.base import (ProcessingError, Processor)


class ProcessingChain:
    """Runs a sequence of processors over records."""

    def __init__(self, processors: list[Processor] | None = None) -> None:
        self.processors: list[Processor] = list(processors or [])
        self.rejected: list[dict[str, Any]] = []

    def add(self, processor: Processor) -> "ProcessingChain":
        self.processors.append(processor)
        return self

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        """Runs the chain over one record (rejects on ProcessingError)."""
        current = dict(record)
        try:
            for processor in self.processors:
                current = processor.apply(current)
            return current
        except ProcessingError:
            self.rejected.append(dict(record))
            raise

    def apply_many(self, records: list[dict[str, Any]],
                   keep_rejected: bool = False) -> list[dict[str, Any]]:
        """Runs the chain over many records, skipping failures."""
        results: list[dict[str, Any]] = []
        for record in records:
            try:
                results.append(self.apply(record))
            except ProcessingError:
                if keep_rejected:
                    results.append(dict(record))
        return results

    def __len__(self) -> int:
        return len(self.processors)
