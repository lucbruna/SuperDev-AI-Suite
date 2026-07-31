"""Logging engine (Volume 37, Fase 4)."""

from __future__ import annotations

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import LogEntry
from devops_engine.logging.log_analyzer import LogAnalyzer
from devops_engine.logging.log_collector import LogCollector
from devops_engine.logging.log_index import LogIndex


class LoggingEngine:
    """Facade over log collection, search and analysis."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.collector = LogCollector()
        self.index = LogIndex()
        self.analyzer = LogAnalyzer()

    def collect(self, source: str, message: str, level: str = "info",
                host: str = "") -> LogEntry:
        entry = self.collector.collect(source, message, level, host)
        self.index.index(entry)
        self.events.publish(DevopsEventType.LOG_COLLECTED,
                            {"log_id": entry.log_id, "source": source})
        self.metrics.increment("devops.logs.collected")
        return entry

    def search(self, query: str, level: str | None = None,
               source: str | None = None,
               limit: int = 50) -> list[LogEntry]:
        return self.index.search(query, level, source, limit)

    def analyze(self, entries: list[LogEntry] | None = None) -> dict:
        return self.analyzer.summary(
            entries if entries is not None else self.collector.entries())

    def stats(self) -> dict[str, int]:
        return {
            "entries": self.collector.count(),
            "indexed_tokens": self.index.count(),
        }
