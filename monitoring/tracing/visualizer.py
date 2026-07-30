from __future__ import annotations

import json
from typing import Any

from ..monitoring_models import Span, Trace


class TraceVisualizer:
    """Produces visual representations of traces."""

    @staticmethod
    def to_text(trace: Trace, show_tags: bool = False) -> str:
        lines: list[str] = [
            f"Trace: {trace.trace_id[:16]}...",
            f"Service: {trace.service_name}",
            f"Spans: {len(trace.spans)}",
        ]

        sorted_spans = sorted(trace.spans, key=lambda s: s.start_time)
        for span in sorted_spans:
            depth = TraceVisualizer._depth(span, sorted_spans)
            indent = "  " * depth
            duration = (
                (span.end_time - span.start_time) * 1000
                if span.end_time
                else 0
            )
            status_mark = (
                "\u2713" if span.status.value == "ok" else "\u2717"
            )
            lines.append(
                f"{indent}{status_mark} {span.operation_name} "
                f"({duration:.1f}ms)"
            )
            if show_tags and span.tags:
                for k, v in span.tags.items():
                    lines.append(f"{indent}  {k}={v}")

        return "\n".join(lines)

    @staticmethod
    def to_json(trace: Trace, indent: int = 2) -> str:
        return json.dumps(
            TraceVisualizer._trace_to_dict(trace),
            indent=indent,
            default=str,
        )

    @staticmethod
    def _trace_to_dict(trace: Trace) -> dict[str, Any]:
        return {
            "trace_id": trace.trace_id,
            "service_name": trace.service_name,
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "duration_ms": round(
                (trace.end_time - trace.start_time) * 1000
            ) if trace.end_time else 0,
            "spans": [
                {
                    "span_id": s.span_id,
                    "parent_span_id": s.parent_span_id or None,
                    "operation_name": s.operation_name,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "duration_ms": round(
                        (s.end_time - s.start_time) * 1000
                    ) if s.end_time else 0,
                    "status": s.status.value,
                    "tags": s.tags,
                }
                for s in trace.spans
            ],
        }

    @staticmethod
    def to_mermaid_timeline(trace: Trace) -> str:
        lines: list[str] = ["timeline"]
        sorted_spans = sorted(trace.spans, key=lambda s: s.start_time)
        for span in sorted_spans:
            duration_ms = round(
                (span.end_time - span.start_time) * 1000
            ) if span.end_time else 0
            lines.append(
                f"    {span.operation_name} : {duration_ms}ms"
            )
        return "\n".join(lines)

    @staticmethod
    def _depth(span: Span, all_spans: list[Span]) -> int:
        depth = 0
        current = span
        seen: set[str] = set()
        while current.parent_span_id and current.parent_span_id not in seen:
            seen.add(current.parent_span_id)
            parent = next(
                (s for s in all_spans if s.span_id == current.parent_span_id),
                None,
            )
            if parent is None:
                break
            depth += 1
            current = parent
        return depth
