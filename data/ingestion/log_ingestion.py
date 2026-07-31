from __future__ import annotations

import glob
import time
from typing import Any

from ..data_models import DataSourceType, LogEntry, LogLevel
from .collector import BaseCollector


class LogCollector(BaseCollector):
    """Collector for log data.

    Collects structured log entries pushed via :meth:`add_entry` or read from
    log files matched by ``patterns`` in the config (glob syntax).
    """

    def __init__(
        self,
        name: str,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self._entries: list[LogEntry] = []

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.LOG

    def add_entry(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        logger: str = "",
        labels: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> LogEntry:
        entry = LogEntry(
            message=message,
            level=level,
            logger=logger or self.name,
            labels=labels or {},
            extra=extra or {},
        )
        self._entries.append(entry)
        return entry

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        config = config or {}
        patterns = config.get("patterns") or self.config.get("patterns") or []
        min_level = config.get("min_level") or self.config.get("min_level")

        rows: list[dict[str, Any]] = []
        for pattern in patterns:
            for path in glob.glob(pattern):
                rows.extend(self._parse_file(path))

        entries = list(self._entries)
        if config.get("clear", True):
            self._entries.clear()
        rows.extend([
            {
                "message": entry.message,
                "level": entry.level.value,
                "logger": entry.logger,
                "timestamp": entry.timestamp,
            }
            for entry in entries
        ])

        if min_level:
            levels = [item.value for item in LogLevel]
            min_index = levels.index(min_level) if min_level in levels else 0
            rows = [row for row in rows if levels.index(row.get("level", "info")) >= min_index]

        return self._build_batch(rows, metadata={"collector": "log"})

    def _parse_file(self, path: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, start=1):
                    line = line.rstrip("\n")
                    if not line.strip():
                        continue
                    level = self._infer_level(line)
                    rows.append({
                        "file": path,
                        "line": line_number,
                        "level": level,
                        "message": line,
                        "timestamp": time.time(),
                    })
        except OSError:
            return []
        return rows

    @staticmethod
    def _infer_level(line: str) -> str:
        lowered = line.lower()
        for token, level in [
            ("critical", "critical"),
            ("error", "error"),
            ("warn", "warn"),
            ("warning", "warn"),
            ("debug", "debug"),
            ("info", "info"),
        ]:
            if token in lowered:
                return level
        return "info"


__all__ = ["LogCollector"]
