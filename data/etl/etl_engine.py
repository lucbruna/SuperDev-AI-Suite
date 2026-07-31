from __future__ import annotations

import time
from typing import Any

from ..data_models import DataRecord, EtlJob, EtlJobStatus


class EtlEngine:
    """ETL/ELT — extract, transform, load jobs with scheduling and monitoring."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.etl
        self._jobs: dict[str, EtlJob] = {}
        self._runs: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def create_job(
        self,
        name: str,
        extract: dict[str, Any],
        transform: dict[str, Any] | None = None,
        load: dict[str, Any] | None = None,
        schedule: str = "",
    ) -> EtlJob:
        job = EtlJob(
            name=name,
            extract=extract,
            transform=transform or {},
            load=load or {},
            schedule=schedule,
        )
        self._jobs[job.job_id] = job
        self.engine.registry.register_etl_job(job)
        return job

    def get_job(self, job_id: str) -> EtlJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[EtlJob]:
        return list(self._jobs.values())

    async def run_job(self, job_id: str) -> dict[str, Any]:
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"ETL job not found: {job_id}")

        job.status = EtlJobStatus.RUNNING
        started = time.perf_counter()
        self.engine.metrics.increment("etl.jobs")

        try:
            rows = await self._extract(job.extract)
            transformed = self._transform(rows, job.transform)
            loaded = await self._load(transformed, job.load)
            job.status = EtlJobStatus.SUCCEEDED
            result = {"status": "succeeded", "rows": loaded}
        except Exception as exc:
            job.status = EtlJobStatus.FAILED
            result = {"status": "failed", "error": str(exc)}

        job.last_run_at = time.time()
        self._runs[job_id] = {
            **result,
            "duration_ms": (time.perf_counter() - started) * 1000,
            "finished_at": job.last_run_at,
        }
        await self.engine.event_bus.emit("data.etl_run", {
            "job_id": job_id,
            "status": result["status"],
        })
        return self._runs[job_id]

    async def _extract(self, extract: dict[str, Any]) -> list[dict[str, Any]]:
        source = extract.get("source", "")
        count = int(extract.get("count", 0))
        connector = self.engine.registry.get_connector(source)
        if connector is not None and hasattr(connector, "read"):
            return await connector.read(extract.get("query", {}))
        return [{"id": i, "value": i} for i in range(count)]

    def _transform(self, rows: list[dict[str, Any]], transform: dict[str, Any]) -> list[dict[str, Any]]:
        if not transform:
            return rows
        result = []
        for row in rows:
            new_row = dict(row)
            for field, expr in transform.items():
                if expr == "double" and isinstance(new_row.get(field), (int, float)):
                    new_row[field] = new_row[field] * 2
                elif expr == "upper" and isinstance(new_row.get(field), str):
                    new_row[field] = new_row[field].upper()
            result.append(new_row)
        return result

    async def _load(self, rows: list[dict[str, Any]], load: dict[str, Any]) -> int:
        table = load.get("table", "default")
        records = [
            DataRecord(source="etl", data=dict(r), metadata={"job": load.get("job", "")})
            for r in rows
        ]
        await self.engine.warehouse.insert(table, records)
        return len(records)

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "jobs": len(self._jobs),
            "runs": len(self._runs),
        }


__all__ = ["EtlEngine"]
