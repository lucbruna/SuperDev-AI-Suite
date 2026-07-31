"""Data Platform Metrics — Metrics tracking for data platform operations."""
from typing import Dict, Any, List
from datetime import datetime


class DataPlatformMetrics:
    def __init__(self):
        self._records_ingested: int = 0
        self._records_processed: int = 0
        self._pipelines_run: int = 0
        self._pipelines_failed: int = 0
        self._quality_checks: int = 0
        self._quality_failures: int = 0
        self._queries_executed: int = 0
        self._bytes_stored: int = 0
        self._events: List[Dict[str, Any]] = []

    def record_ingestion(self, count: int = 1) -> None:
        self._records_ingested += count

    def record_processing(self, count: int = 1) -> None:
        self._records_processed += count

    def record_pipeline_start(self) -> None:
        self._pipelines_run += 1

    def record_pipeline_failure(self) -> None:
        self._pipelines_failed += 1

    def record_quality_check(self, passed: bool = True) -> None:
        self._quality_checks += 1
        if not passed:
            self._quality_failures += 1

    def record_query(self) -> None:
        self._queries_executed += 1

    def record_bytes(self, count: int) -> None:
        self._bytes_stored += count

    def add_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        self._events.append({
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        })

    def get_stats(self) -> Dict[str, Any]:
        return {
            "records_ingested": self._records_ingested,
            "records_processed": self._records_processed,
            "pipelines_run": self._pipelines_run,
            "pipelines_failed": self._pipelines_failed,
            "quality_checks": self._quality_checks,
            "quality_failures": self._quality_failures,
            "queries_executed": self._queries_executed,
            "bytes_stored": self._bytes_stored,
            "events": len(self._events),
        }

    @property
    def quality_rate(self) -> float:
        if self._quality_checks == 0:
            return 100.0
        return ((self._quality_checks - self._quality_failures) / self._quality_checks) * 100

    @property
    def pipeline_success_rate(self) -> float:
        if self._pipelines_run == 0:
            return 100.0
        return ((self._pipelines_run - self._pipelines_failed) / self._pipelines_run) * 100
