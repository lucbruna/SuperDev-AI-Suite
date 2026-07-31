from __future__ import annotations

import json

import pytest

from SuperDev.data.ingestion.file_ingestion import FileCollector, FileConnector


@pytest.fixture
def csv_path(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id,name\n1,ana\n2,bob\n", encoding="utf-8")
    return str(path)


@pytest.fixture
def json_path(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps([{"id": 1, "v": "a"}, {"id": 2, "v": "b"}]), encoding="utf-8")
    return str(path)


@pytest.fixture
def jsonl_path(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text(
        json.dumps({"id": 1}) + "\n" + json.dumps({"id": 2}) + "\n",
        encoding="utf-8",
    )
    return str(path)


class TestFileConnector:
    @pytest.mark.asyncio
    async def test_connect_missing_file(self) -> None:
        connector = FileConnector("f", {"path": "does-not-exist.csv"})
        assert await connector.connect() is False

    @pytest.mark.asyncio
    async def test_read_csv(self, csv_path) -> None:
        connector = FileConnector("f", {"path": csv_path})
        assert await connector.connect()
        rows = await connector.read()
        assert rows == [{"id": "1", "name": "ana"}, {"id": "2", "name": "bob"}]

    @pytest.mark.asyncio
    async def test_read_json(self, json_path) -> None:
        connector = FileConnector("f", {"path": json_path})
        await connector.connect()
        rows = await connector.read()
        assert rows[0]["v"] == "a"

    @pytest.mark.asyncio
    async def test_read_jsonl(self, jsonl_path) -> None:
        connector = FileConnector("f", {"path": jsonl_path})
        await connector.connect()
        rows = await connector.read()
        assert len(rows) == 2

    @pytest.mark.asyncio
    async def test_read_missing_file_raises(self) -> None:
        connector = FileConnector("f", {"path": "nope.csv"})
        with pytest.raises(FileNotFoundError):
            await connector.read()

    @pytest.mark.asyncio
    async def test_base_dir_blocks_escape(self, tmp_path) -> None:
        # CWE-22 regression: paths outside base_dir must be refused.
        outside = tmp_path / "secret.csv"
        outside.write_text("id\n1\n", encoding="utf-8")
        (tmp_path / "data").mkdir(exist_ok=True)
        connector = FileConnector(
            "f", {"path": "../secret.csv", "base_dir": str(tmp_path / "data")})
        with pytest.raises(ValueError, match="escapes"):
            await connector.read()

    @pytest.mark.asyncio
    async def test_base_dir_allows_internal_path(self, tmp_path) -> None:
        inner = tmp_path / "data" / "ok.csv"
        inner.parent.mkdir(exist_ok=True)
        inner.write_text("id,name\n1,ana\n", encoding="utf-8")
        connector = FileConnector(
            "f", {"path": "ok.csv", "base_dir": str(tmp_path / "data")})
        rows = await connector.read()
        assert rows == [{"id": "1", "name": "ana"}]


class TestFileCollector:
    @pytest.mark.asyncio
    async def test_collect_csv(self, csv_path) -> None:
        connector = FileConnector("f", {"path": csv_path})
        collector = FileCollector("file-source", connector=connector)
        batch = await collector.collect()
        assert len(batch.records) == 2
        assert batch.records[0].data["name"] == "ana"
