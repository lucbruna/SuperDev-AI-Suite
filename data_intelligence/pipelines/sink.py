"""Pipeline sink stage (send results to dashboards/warehouse/reports)."""

from __future__ import annotations

from typing import Any

from data_intelligence.pipelines.base import PipelineError, PipelineStage


class SinkStage(PipelineStage):
    """Delivers the pipeline output to a destination.

    Config:
        * ``destination`` - "dashboard" | "warehouse" | "report" | "none".
        * ``sink``        - optional DataSink-like object with ``write``.
        * ``target``      - destination identifier passed to ``write``.
    """

    stage_type = "sink"

    def __init__(self, destination: str = "none", sink: Any = None,
                 target: str | None = None, **config: Any) -> None:
        super().__init__(destination=destination, sink=sink, target=target,
                         **config)
        self.destination = destination
        self.sink = sink
        self.target = target

    def run(self, records: list[dict[str, Any]],
            context: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                              dict[str, Any]]:
        if self.destination in ("none", ""):
            context["sink"] = {"destination": "none",
                               "written": len(records)}
            return records, context
        if self.sink is None or not hasattr(self.sink, "write"):
            raise PipelineError(
                "SinkStage requires a sink with write()")
        result = self.sink.write(records, self.target or self.destination)
        context["sink"] = result
        return records, context
