"""Pipeline transformation stage (mapping, renaming, casting)."""

from __future__ import annotations

from typing import Any, Callable

from data_intelligence.data_protocols import coerce_number
from data_intelligence.pipelines.base import PipelineStage


class TransformationStage(PipelineStage):
    """Transforms records field by field.

    Config:
        * ``rename``   - mapping {new_field: old_field}.
        * ``casts``    - mapping {field: "number"|"text"|"bool"}.
        * ``functions``- mapping {field: callable(value) -> value}.
        * ``drop``     - list of fields to remove from the output.
    """

    stage_type = "transformation"

    def __init__(self, rename: dict[str, str] | None = None,
                 casts: dict[str, str] | None = None,
                 functions: dict[str, Callable[[Any], Any]] | None = None,
                 drop: list[str] | None = None, **config: Any) -> None:
        super().__init__(rename=rename, casts=casts, functions=functions,
                         drop=drop, **config)
        self.rename = rename or {}
        self.casts = casts or {}
        self.functions = functions or {}
        self.drop = drop or []

    def run(self, records: list[dict[str, Any]],
            context: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                              dict[str, Any]]:
        transformed: list[dict[str, Any]] = []
        for record in records:
            out: dict[str, Any] = {}
            for new_field, old_field in self.rename.items():
                if old_field in record:
                    out[new_field] = record[old_field]
            for field, value in record.items():
                if field in self.drop or field in self.rename.values():
                    continue
                if field not in out:
                    out[field] = value
            for field, kind in self.casts.items():
                if field in out:
                    out[field] = self._cast(out[field], kind)
            for field, fn in self.functions.items():
                if field in out:
                    out[field] = fn(out[field])
            transformed.append(out)
        return transformed, context

    @staticmethod
    def _cast(value: Any, kind: str) -> Any:
        if kind in ("number", "int", "float"):
            return coerce_number(value)
        if kind == "bool":
            return bool(value)
        return str(value)
