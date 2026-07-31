from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any

from ..data_models import DataSourceType
from .collector import BaseCollector
from .connector import BaseConnector


class FileConnector(BaseConnector):
    """File connector supporting CSV, JSON and newline-delimited JSON.

    Config keys:
        path: path to the file
        format: optional "csv" | "json" | "jsonl" (inferred from extension)
        encoding: file encoding (default "utf-8")
    """

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.FILE

    def _safe_path(self, raw: str | Path) -> Path:
        """Resolve *raw* inside ``base_dir`` when configured (CWE-22 guard).

        Without a ``base_dir`` the connector keeps its original behaviour and
        may read any path the process can access.
        """
        candidate = Path(raw)
        base_dir = self.config.get("base_dir")
        if not base_dir:
            return candidate
        root = Path(base_dir).resolve()
        resolved = candidate if candidate.is_absolute() else root / candidate
        resolved = resolved.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError(
                f"File connector '{self.name}' path escapes base_dir: {raw!r}")
        return resolved

    async def connect(self) -> bool:
        raw = self.config.get("path")
        self.connected = bool(raw) and self._safe_path(raw).exists()
        return self.connected

    async def read(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        path = self._safe_path(query.get("path") or self.config["path"])
        if not path.exists():
            raise FileNotFoundError(f"File connector '{self.name}' file not found: {path}")

        data_format = query.get("format") or self.config.get("format")
        if data_format is None:
            suffix = path.suffix.lower().lstrip(".")
            data_format = "jsonl" if suffix in ("jsonl", "ndjson") else suffix

        encoding = query.get("encoding") or self.config.get("encoding", "utf-8")
        rows: list[dict[str, Any]]

        if data_format == "csv":
            rows = self._read_csv(path, encoding)
        elif data_format == "jsonl":
            rows = self._read_jsonl(path, encoding)
        else:  # json or fallback
            rows = self._read_json(path, encoding)

        self._last_read_at = time.time()
        return rows

    @staticmethod
    def _read_csv(path: Path, encoding: str) -> list[dict[str, Any]]:
        with path.open("r", encoding=encoding, newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _read_json(path: Path, encoding: str) -> list[dict[str, Any]]:
        with path.open("r", encoding=encoding) as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return [dict(item) for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            items = payload.get("results") or payload.get("data") or payload.get("items") or []
            return [dict(item) for item in items if isinstance(item, dict)]
        return []

    @staticmethod
    def _read_jsonl(path: Path, encoding: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding=encoding) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if isinstance(item, dict):
                    rows.append(item)
        return rows

    async def disconnect(self) -> None:
        self.connected = False


class FileCollector(BaseCollector):
    """Collector that reads records from a file via :class:`FileConnector`."""

    def __init__(
        self,
        name: str,
        connector: FileConnector | None = None,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self.connector = connector or FileConnector(name, config or {})

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.FILE

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        merged = {**self.config, **(config or {})}
        await self.connector.connect()
        try:
            rows = await self.connector.read(merged)
        finally:
            await self.connector.disconnect()
        return self._build_batch(rows, metadata={"connector": "file"})


__all__ = ["FileConnector", "FileCollector"]
