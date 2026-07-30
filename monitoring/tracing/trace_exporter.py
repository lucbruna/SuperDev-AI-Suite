from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any

from ..monitoring_models import Span, Trace


class TraceExporter(ABC):
    """Abstract base for trace exporters."""

    @abstractmethod
    def export(self, trace: Trace) -> None: ...


class ConsoleTraceExporter(TraceExporter):
    """Exports traces to stdout as structured text."""

    def export(self, trace: Trace) -> None:
        print(f"Trace {trace.trace_id} ({trace.service_name})")
        for span in trace.spans:
            status = span.status.value
            duration = (span.end_time - span.start_time) * 1000 if span.end_time else 0
            print(
                f"  [{status}] {span.operation_name} "
                f"(span={span.span_id[:8]} parent={span.parent_span_id[:8] or 'none'}) "
                f"{duration:.1f}ms"
            )


class JsonFileTraceExporter(TraceExporter):
    """Exports traces to a JSON file."""

    def __init__(self, file_path: str, append: bool = False) -> None:
        self._file_path = file_path
        self._append = append

    def export(self, trace: Trace) -> None:
        data = self._trace_to_dict(trace)
        mode = "a" if self._append else "w"
        os.makedirs(os.path.dirname(self._file_path) or ".", exist_ok=True)
        with open(self._file_path, mode, encoding="utf-8") as f:
            f.write(json.dumps(data, default=str) + "\n")

    @staticmethod
    def _trace_to_dict(trace: Trace) -> dict[str, Any]:
        return {
            "trace_id": trace.trace_id,
            "service_name": trace.service_name,
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "spans": [
                {
                    "span_id": s.span_id,
                    "trace_id": s.trace_id,
                    "parent_span_id": s.parent_span_id,
                    "operation_name": s.operation_name,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "status": s.status.value,
                    "tags": s.tags,
                    "logs": s.logs,
                }
                for s in trace.spans
            ],
        }


class BatchTraceExporter(TraceExporter):
    """Batches traces and exports in bulk."""

    def __init__(self, exporter: TraceExporter, batch_size: int = 10) -> None:
        self._inner = exporter
        self._batch_size = batch_size
        self._buffer: list[Trace] = []

    def export(self, trace: Trace) -> None:
        self._buffer.append(trace)
        if len(self._buffer) >= self._batch_size:
            self.flush()

    def flush(self) -> None:
        for trace in self._buffer:
            self._inner.export(trace)
        self._buffer.clear()
