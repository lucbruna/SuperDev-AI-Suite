"""Tests for the ingestion subsystem (Volume 22, Fase 2)."""

from __future__ import annotations

import json
import sqlite3

import pytest

from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_factory import build_engine
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import SourceType
from data_intelligence.ingestion.api_source import ApiSource
from data_intelligence.ingestion.collector import IngestionCollector
from data_intelligence.ingestion.erp_crm_source import CrmSource, ErpSource
from data_intelligence.ingestion.file_source import FileSource
from data_intelligence.ingestion.nosql_source import MongoSource
from data_intelligence.ingestion.sql_source import SqlSource
from data_intelligence.ingestion.stream_source import StreamSource


def make_collector() -> IngestionCollector:
    events = DataIntelligenceEvents()
    metrics = DataIntelligenceMetrics()
    return IngestionCollector(events=events, metrics=metrics,
                              config=None, context=DataIntelligenceContext())


class FakeCollection:
    """Duck-typed pymongo collection."""

    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def find(self, query: dict) -> FakeCursor:
        return FakeCursor([d for d in self._docs
                           if all(d.get(k) == v for k, v in query.items())])


class FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def limit(self, n: int) -> FakeCursor:
        return FakeCursor(self._docs[:n])

    def __iter__(self):
        return iter(self._docs)


class TestSqlSource:
    def test_sqlite_roundtrip(self, tmp_path) -> None:
        db = tmp_path / "test.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE vendas (id INTEGER, valor REAL)")
        conn.executemany("INSERT INTO vendas VALUES (?, ?)",
                         [(1, 100.0), (2, 200.0)])
        conn.commit()
        conn.close()

        source = SqlSource("s-sql", "Vendas DB", dsn=str(db),
                           query="SELECT * FROM vendas")
        rows = list(source.fetch(source))
        assert len(rows) == 2
        assert rows[0]["valor"] == 100.0
        records = source.records(rows, tags=["vendas"])
        assert len(records) == 2
        assert records[0].source_id == "s-sql"

    def test_requires_dsn_or_connector(self) -> None:
        source = SqlSource("s-sql", "No DSN")
        try:
            list(source.fetch(source))
            raised = False
        except RuntimeError:
            raised = True
        assert raised is True

    def test_custom_connector(self) -> None:
        def connector(_src):
            return [{"a": 1}, {"a": 2}], None

        source = SqlSource("s-sql", "Custom", connector=connector)
        assert list(source.fetch(source)) == [{"a": 1}, {"a": 2}]


class TestMongoSource:
    def test_fetch_filter_limit(self) -> None:
        collection = FakeCollection([{"nome": "ana", "uf": "SP"},
                                     {"nome": "bia", "uf": "SP"},
                                     {"nome": "caio", "uf": "RJ"}])
        source = MongoSource("s-mongo", "Clientes", collection,
                             filter_query={"uf": "SP"}, limit=1)
        rows = list(source.fetch(source))
        assert rows == [{"nome": "ana", "uf": "SP"}]

    def test_requires_collection(self) -> None:
        source = MongoSource("s-mongo", "Sem coleção", None)
        try:
            list(source.fetch(source))
            raised = False
        except RuntimeError:
            raised = True
        assert raised is True


class TestApiSource:
    def test_custom_requester(self) -> None:
        def requester(endpoint, headers):  # noqa: ARG001
            return {"data": [{"id": 1}, {"id": 2}]}

        source = ApiSource("s-api", "API Vendas", "https://api.example.com",
                           requester=requester)
        rows = list(source.fetch(source))
        assert len(rows) == 2
        assert rows[0]["id"] == 1

    def test_requester_list_response(self) -> None:
        source = ApiSource("s-api", "API", "https://x.test",
                           requester=lambda endpoint, headers: [{"v": 1}])  # noqa: ARG005
        assert list(source.fetch(source)) == [{"v": 1}]

    def test_blocks_private_endpoint(self) -> None:
        # CWE-918 regression: default requester must refuse metadata targets.
        source = ApiSource("s-api", "Metadata",
                           "http://169.254.169.254/latest/meta-data/")
        with pytest.raises(ValueError, match="internal"):
            list(source.fetch(source))


class TestFileSource:
    def test_csv(self, tmp_path) -> None:
        path = tmp_path / "vendas.csv"
        path.write_text("produto,valor\nA,10\nB,20\n", encoding="utf-8")
        source = FileSource("s-file", "CSV", path)
        rows = list(source.fetch(source))
        assert rows == [{"produto": "A", "valor": "10"},
                        {"produto": "B", "valor": "20"}]

    def test_json_list(self, tmp_path) -> None:
        path = tmp_path / "vendas.json"
        path.write_text(json.dumps([{"v": 1}, {"v": 2}]), encoding="utf-8")
        source = FileSource("s-file", "JSON", path)
        assert list(source.fetch(source)) == [{"v": 1}, {"v": 2}]

    def test_json_data_key(self, tmp_path) -> None:
        path = tmp_path / "payload.json"
        path.write_text(json.dumps({"data": [{"v": 5}]}), encoding="utf-8")
        source = FileSource("s-file", "JSON", path)
        assert list(source.fetch(source)) == [{"v": 5}]

    def test_missing_file(self, tmp_path) -> None:
        source = FileSource("s-file", "Missing", tmp_path / "nope.csv")
        try:
            list(source.fetch(source))
            raised = False
        except FileNotFoundError:
            raised = True
        assert raised is True

    def test_write_csv(self, tmp_path) -> None:
        source = FileSource("s-file", "CSV", tmp_path / "empty.csv")
        target = tmp_path / "out.csv"
        result = source.write_csv([{"a": 1, "b": 2}, {"a": 3, "b": 4}],
                                  target)
        assert result["written"] == 2
        back = FileSource("s-file", "CSV", target)
        assert list(back.fetch(back)) == [{"a": "1", "b": "2"},
                                          {"a": "3", "b": "4"}]

    def test_base_dir_blocks_escape(self, tmp_path) -> None:
        # CWE-22 regression: paths outside base_dir must be refused.
        outside = tmp_path / "secret.csv"
        outside.write_text("x\n1\n", encoding="utf-8")
        (tmp_path / "data").mkdir(exist_ok=True)
        source = FileSource("s-file", "Esc", str(outside),
                            base_dir=str(tmp_path / "data"))
        with pytest.raises(ValueError, match="escapes"):
            list(source.fetch(source))


class TestStreamSource:
    def test_emit_fetch_drain(self) -> None:
        source = StreamSource("s-stream", "IoT", keep=0)
        source.emit({"temp": 30.1})
        source.emit_many([{"temp": 31.2}, {"temp": 32.3}])
        assert source.buffer_size() == 3
        rows = list(source.fetch(source))
        assert len(rows) == 3
        assert source.buffer_size() == 0

    def test_keep_tail(self) -> None:
        source = StreamSource("s-stream", "Logs", keep=2)
        source.emit_many([{"line": 1}, {"line": 2}, {"line": 3}])
        rows = list(source.fetch(source))
        assert [r["line"] for r in rows] == [1, 2, 3]
        assert source.buffer_size() == 2


class TestErpCrmSource:
    def test_erp_fetcher(self) -> None:
        def fetcher(module):
            assert module == "sales"
            return [{"produto": "X", "vendas": 10}]

        source = ErpSource("s-erp", "ERP", module="sales", fetcher=fetcher)
        assert list(source.fetch(source)) == [{"produto": "X", "vendas": 10}]

    def test_erp_without_fetcher(self) -> None:
        source = ErpSource("s-erp", "ERP")
        assert list(source.fetch(source)) == []

    def test_crm_fetcher(self) -> None:
        def fetcher(entity):
            assert entity == "contacts"
            return [{"nome": "Ana"}]

        source = CrmSource("s-crm", "CRM", entity="contacts", fetcher=fetcher)
        assert list(source.fetch(source)) == [{"nome": "Ana"}]


class TestCollector:
    def test_add_and_fetch(self) -> None:
        collector = make_collector()
        source = StreamSource("s-stream", "IoT")
        source.emit({"temp": 20.0})
        collector.add_source(source)
        records = collector.fetch("s-stream", tags=["iot"])
        assert len(records) == 1
        assert records[0].tags == ["iot"]
        assert collector.latest_batch("s-stream")[0].data["temp"] == 20.0

    def test_fetch_unknown_source(self) -> None:
        collector = make_collector()
        try:
            collector.fetch("ghost")
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_ingest_with_records(self) -> None:
        collector = make_collector()
        collector.add_source(StreamSource("s-stream", "IoT"))
        source = build_engine().manager.register_source(
            "s-stream", "IoT", SourceType.STREAM)
        result = collector.ingest(source, [{"v": 1}, {"v": 2}])
        assert result["ingested"] == 2
        assert len(result["records"]) == 2
        assert result["records"][0].data == {"v": 1}

    def test_ingest_fetch_from_connector(self) -> None:
        collector = make_collector()
        collector.add_source(StreamSource("s-stream", "IoT"))
        source = build_engine().manager.register_source(
            "s-stream", "IoT", SourceType.STREAM)
        collector.fetch("s-stream")  # empty batch first
        stream = collector.sources["s-stream"]
        assert isinstance(stream, StreamSource)
        stream.emit({"v": 9})
        result = collector.ingest(source)
        assert result["ingested"] == 1
        assert result["records"][0].data == {"v": 9}

    def test_engine_integration(self) -> None:
        engine = build_engine()
        collector = IngestionCollector(events=engine.events,
                                       metrics=engine.metrics,
                                       config=engine.config,
                                       context=engine.context)
        collector.add_source(StreamSource("s-iot", "IoT"))
        engine.attach_subsystem("ingestion", collector)
        engine.register_source("s-iot", "IoT", SourceType.STREAM)
        result = engine.ingest("s-iot", [{"temp": 22.5}, {"temp": 23.5}])
        assert result["ingested"] == 2
        assert engine.manager.ingestion_engine is collector
        stats = collector.stats()
        assert "s-iot" in stats["sources"]
        assert engine.registry.stats()["sources"] == 1

    def test_collector_stats(self) -> None:
        collector = make_collector()
        assert collector.stats()["sources"] == []
        collector.add_source(StreamSource("a", "A"))
        assert collector.stats()["sources"] == ["a"]
