"""Pipeline indicator stage (compute KPI metrics)."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_protocols import numeric_values
from data_intelligence.pipelines.base import PipelineStage


class IndicatorStage(PipelineStage):
    """Computes aggregate indicators over the records.

    Config:
        * ``value_field`` - numeric field aggregated (required).
        * ``aggregations`` - list of "total"|"count"|"average"|"min"|"max".
        * ``group_by``    - optional field used to segment the indicators.

    The indicators are stored in ``context["indicators"]`` and also
    returned as indicator records tagged ``indicator``.
    """

    stage_type = "indicator"

    def __init__(self, value_field: str = "value",
                 aggregations: list[str] | None = None,
                 group_by: str | None = None, **config: Any) -> None:
        super().__init__(value_field=value_field,
                         aggregations=aggregations, group_by=group_by,
                         **config)
        self.value_field = value_field
        self.aggregations = aggregations or ["total", "count"]
        self.group_by = group_by

    def run(self, records: list[dict[str, Any]],
            context: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                              dict[str, Any]]:
        if self.group_by:
            indicators = self._grouped(records)
        else:
            indicators = [self._aggregate(records, {})]
        context["indicators"] = indicators
        tagged = [dict(record, tags=["indicator"]) for record in indicators]
        return tagged, context

    def _aggregate(self, records: list[dict[str, Any]],
                   group: dict[str, Any]) -> dict[str, Any]:
        values = numeric_values(records, self.value_field)
        result: dict[str, Any] = dict(group)
        if "total" in self.aggregations:
            result["total"] = round(sum(values), 4) if values else 0.0
        if "count" in self.aggregations:
            result["count"] = len(records)
        if "average" in self.aggregations:
            result["average"] = (round(sum(values) / len(values), 4)
                                 if values else 0.0)
        if "min" in self.aggregations:
            result["min"] = min(values) if values else None
        if "max" in self.aggregations:
            result["max"] = max(values) if values else None
        return result

    def _grouped(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        group_field: str = self.group_by or "group"
        buckets: dict[Any, list[dict[str, Any]]] = {}
        for record in records:
            key = record.get(group_field, "unknown")
            buckets.setdefault(key, []).append(record)
        return [self._aggregate(records, {group_field: key})
                for key, records in sorted(buckets.items(),
                                           key=lambda kv: str(kv[0]))]
