"""Validation rules for pipeline definitions."""

from __future__ import annotations

from typing import Any


class PipelineValidator:
    """Checks that a pipeline definition is well-formed."""

    def validate(self, pipeline: Any) -> list[str]:
        issues: list[str] = []
        if not pipeline.pipeline_id:
            issues.append("pipeline_id is required")
        if not pipeline.name:
            issues.append("name is required")
        if not pipeline.stages:
            issues.append("pipeline has no stages")
            return issues
        if pipeline.on_failure not in {"stop", "continue"}:
            issues.append(f"on_failure must be 'stop' or 'continue', "
                          f"got '{pipeline.on_failure}'")
        ids = [s.stage_id for s in pipeline.stages]
        if any(not sid for sid in ids):
            issues.append("every stage must have a stage_id")
        if len(set(ids)) != len(ids):
            issues.append("duplicate stage ids")
        for stage in pipeline.stages:
            for ref in (stage.next_on_success, stage.next_on_failure):
                if ref and ref not in ids:
                    issues.append(f"unknown stage '{ref}' referenced by "
                                  f"'{stage.stage_id}'")
        return issues
