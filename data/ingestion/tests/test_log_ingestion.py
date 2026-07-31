from __future__ import annotations

import pytest

from SuperDev.data.data_models import LogLevel
from SuperDev.data.ingestion.log_ingestion import LogCollector


class TestLogCollector:
    @pytest.mark.asyncio
    async def test_add_and_collect(self) -> None:
        collector = LogCollector("logs")
        collector.add_entry("started", level=LogLevel.INFO)
        collector.add_entry("failed", level=LogLevel.ERROR)
        batch = await collector.collect()
        assert len(batch.records) == 2
        levels = {r.data["level"] for r in batch.records}
        assert levels == {"info", "error"}

    @pytest.mark.asyncio
    async def test_min_level_filter(self) -> None:
        collector = LogCollector("logs")
        collector.add_entry("debug", level=LogLevel.DEBUG)
        collector.add_entry("warn", level=LogLevel.WARN)
        collector.add_entry("error", level=LogLevel.ERROR)
        batch = await collector.collect({"min_level": "warn"})
        assert len(batch.records) == 2
        assert all(r.data["level"] in ("warn", "error") for r in batch.records)

    @pytest.mark.asyncio
    async def test_parse_file_with_inference(self, tmp_path) -> None:
        path = tmp_path / "app.log"
        path.write_text(
            "INFO started\nERROR something broke\nWARN high latency\n",
            encoding="utf-8",
        )
        collector = LogCollector("logs", config={"patterns": [str(path)]})
        batch = await collector.collect()
        assert len(batch.records) == 3
        levels = {r.data["level"] for r in batch.records}
        assert levels == {"info", "error", "warn"}
        assert batch.records[0].data["file"] == str(path)

    @pytest.mark.asyncio
    async def test_infer_level_helper(self) -> None:
        assert LogCollector._infer_level("error: boom") == "error"  # noqa: SLF001
        assert LogCollector._infer_level("regular line") == "info"
