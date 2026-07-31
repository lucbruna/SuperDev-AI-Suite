"""Pipeline cleaning stage (dedupe, drop empties, defaults)."""

from __future__ import annotations

from typing import Any

from data_intelligence.pipelines.base import PipelineStage


class CleaningStage(PipelineStage):
    """Cleans records before processing.

    Config:
        * ``dedupe_key`` - field used to remove duplicate records.
        * ``required``   - list of fields; records missing them are dropped.
        * ``trim``       - whether to strip whitespace from string values.
        * ``defaults``   - mapping of field -> default when missing/empty.
    """

    stage_type = "cleaning"

    def __init__(self, dedupe_key: str | None = None,
                 required: list[str] | None = None, trim: bool = True,
                 defaults: dict[str, Any] | None = None,
                 **config: Any) -> None:
        super().__init__(dedupe_key=dedupe_key, required=required,
                         trim=trim, defaults=defaults, **config)
        self.dedupe_key = dedupe_key
        self.required = required or []
        self.trim = trim
        self.defaults = defaults or {}

    def run(self, records: list[dict[str, Any]],
            context: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                              dict[str, Any]]:
        seen: set[Any] = set()
        cleaned: list[dict[str, Any]] = []
        dropped = {"duplicates": 0, "incomplete": 0}
        for record in records:
            candidate = dict(record)
            if self.trim:
                candidate = {k: v.strip() if isinstance(v, str) else v
                             for k, v in candidate.items()}
            for field, default in self.defaults.items():
                value = candidate.get(field)
                if value is None or value == "":
                    candidate[field] = default
            if self.dedupe_key is not None:
                key = candidate.get(self.dedupe_key)
                if key in seen:
                    dropped["duplicates"] += 1
                    continue
                seen.add(key)
            if self.required and any(
                    candidate.get(field) in (None, "")
                    for field in self.required):
                dropped["incomplete"] += 1
                continue
            cleaned.append(candidate)
        context["cleaning"] = dropped
        return cleaned, context
