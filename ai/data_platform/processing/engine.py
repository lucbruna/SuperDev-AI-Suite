"""Processing engine."""

import uuid
from datetime import datetime
from typing import Any

from .models import ProcessingJob, ProcessingResult, ProcessingStatus, TransformRule, TransformType


class ProcessingEngine:
    def __init__(self):
        self._jobs: dict[str, ProcessingJob] = {}
        self._results: list[ProcessingResult] = []
        self._rules: dict[str, TransformRule] = {}

    def create_rule(self, rule: TransformRule) -> TransformRule:
        self._rules[rule.rule_id] = rule
        return rule

    def get_rule(self, rule_id: str) -> TransformRule | None:
        return self._rules.get(rule_id)

    def create_job(self, job: ProcessingJob) -> ProcessingJob:
        self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> ProcessingJob | None:
        return self._jobs.get(job_id)

    def start_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = ProcessingStatus.RUNNING
        job.started_at = datetime.now()
        return True

    def complete_job(self, job_id: str, output_count: int = 0) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = ProcessingStatus.COMPLETED
        job.output_count = output_count
        job.completed_at = datetime.now()
        result = ProcessingResult(
            result_id=str(uuid.uuid4())[:8],
            job_id=job_id,
            status=ProcessingStatus.COMPLETED,
            records_in=job.input_count,
            records_out=output_count,
        )
        self._results.append(result)
        return True

    def fail_job(self, job_id: str, error: str = "Unknown error") -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = ProcessingStatus.FAILED
        job.error_count += 1
        result = ProcessingResult(
            result_id=str(uuid.uuid4())[:8],
            job_id=job_id,
            status=ProcessingStatus.FAILED,
            records_in=job.input_count,
            errors=[error],
        )
        self._results.append(result)
        return True

    def transform_records(self, records: list[dict[str, Any]], rules: list[TransformRule]) -> list[dict[str, Any]]:
        result = list(records)
        for rule in sorted(rules, key=lambda r: r.order):
            if not rule.enabled:
                continue
            if rule.transform_type == TransformType.FILTER:
                field_name = rule.config.get("field", "")
                value = rule.config.get("value")
                result = [r for r in result if r.get(field_name) == value]
            elif rule.transform_type == TransformType.MAP:
                mapping = rule.config.get("mapping", {})
                new_result = []
                for r in result:
                    new_r = dict(r)
                    for src, dst in mapping.items():
                        if src in new_r:
                            new_r[dst] = new_r.pop(src)
                    new_result.append(new_r)
                result = new_result
            elif rule.transform_type == TransformType.DEDUPLICATE:
                key = rule.config.get("key", "")
                seen = set()
                deduped = []
                for r in result:
                    k = r.get(key) if key else str(r)
                    if k not in seen:
                        seen.add(k)
                        deduped.append(r)
                result = deduped
        return result

    def aggregate_records(
        self, records: list[dict[str, Any]], group_by: str, agg_field: str, agg_func: str = "sum"
    ) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in records:
            key = str(r.get(group_by, ""))
            groups.setdefault(key, []).append(r)
        results = []
        for key, group in groups.items():
            values = [r.get(agg_field, 0) for r in group if isinstance(r.get(agg_field), (int, float))]
            if agg_func == "sum":
                agg_value = sum(values)
            elif agg_func == "avg":
                agg_value = sum(values) / len(values) if values else 0
            elif agg_func == "count":
                agg_value = len(group)
            elif agg_func == "min":
                agg_value = min(values) if values else 0
            elif agg_func == "max":
                agg_value = max(values) if values else 0
            else:
                agg_value = sum(values)
            results.append({group_by: key, f"{agg_func}_{agg_field}": agg_value, "count": len(group)})
        return results

    def get_results(self, job_id: str | None = None) -> list[ProcessingResult]:
        if job_id:
            return [r for r in self._results if r.job_id == job_id]
        return list(self._results)

    def get_stats(self) -> dict:
        jobs = list(self._jobs.values())
        return {
            "rules": len(self._rules),
            "jobs": len(jobs),
            "completed": len([j for j in jobs if j.status == ProcessingStatus.COMPLETED]),
            "failed": len([j for j in jobs if j.status == ProcessingStatus.FAILED]),
            "results": len(self._results),
        }
