"""Tests for the warehouse and lake subsystems (Volume 22, Fase 4)."""

from __future__ import annotations

from datetime import datetime

from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.lake.catalog import LakeCatalog, LakeEntry
from data_intelligence.lake.compression import Compressor
from data_intelligence.lake.engine import LakeEngine
from data_intelligence.lake.partition import DatePartitioner
from data_intelligence.warehouse.base import WarehouseError
from data_intelligence.warehouse.dimension import DimensionTable
from data_intelligence.warehouse.engine import WarehouseEngine
from data_intelligence.warehouse.fact import FactTable
from data_intelligence.warehouse.loader import StagingArea
from data_intelligence.warehouse.schema import StarSchema


def make_warehouse() -> WarehouseEngine:
    return WarehouseEngine(events=DataIntelligenceEvents(),
                           metrics=DataIntelligenceMetrics(), config=None,
                           context=DataIntelligenceContext())


def make_lake() -> LakeEngine:
    return LakeEngine(events=DataIntelligenceEvents(),
                      metrics=DataIntelligenceMetrics(), config=None,
                      context=DataIntelligenceContext())


class TestWarehouseTable:
    def test_insert_and_get(self) -> None:
        table = DimensionTable("dim_cliente", {"id": "number",
                                               "nome": "text"})
        table.insert({"id": 1, "nome": "Ana"})
        row = table.get(1)
        assert row is not None and row["nome"] == "Ana"
        assert table.count() == 1

    def test_insert_requires_key(self) -> None:
        table = DimensionTable("dim_x", {"id": "number"})
        try:
            table.insert({"nome": "sem id"})
            raised = False
        except WarehouseError:
            raised = True
        assert raised is True

    def test_insert_many_and_truncate(self) -> None:
        table = DimensionTable("dim_x", {"id": "number"})
        assert table.insert_many([{"id": i} for i in range(5)]) == 5
        assert table.count() == 5
        assert table.truncate() == 5
        assert table.count() == 0

    def test_dimension_tracks_changes(self) -> None:
        table = DimensionTable("dim_cliente", {"id": "number",
                                               "nome": "text"},
                               track_changes=True)
        table.upsert({"id": 1, "nome": "Ana"})
        table.upsert({"id": 1, "nome": "Ana Silva"})
        current = table.get(1)
        assert current is not None and current["nome"] == "Ana Silva"
        history = table.history(1)
        assert history == [{"id": 1.0, "nome": "Ana"}]


class TestFactTable:
    def test_rollup(self) -> None:
        table = FactTable("fact_vendas", {"id": "number", "uf": "text",
                                          "valor": "number"},
                          measures=["valor"], dimensions=["uf"])
        table.insert_many([{"id": 1, "uf": "SP", "valor": 10},
                           {"id": 2, "uf": "SP", "valor": 20},
                           {"id": 3, "uf": "RJ", "valor": 5}])
        totals = table.rollup("uf", "valor")
        assert totals == {"SP": 30.0, "RJ": 5.0}


class TestStarSchema:
    def test_load_fact_with_dimensions(self) -> None:
        schema = StarSchema("comercial")
        schema.add_dimension("cliente", {"id": "number", "nome": "text"})
        schema.add_fact("vendas", {"id": "number", "valor": "number"},
                        measures=["valor"], dimensions=["cliente"])
        schema.dimensions["cliente"].insert({"id": 1, "nome": "Ana"})
        count = schema.load_fact(
            "vendas",
            [{"id": 10, "valor": 100, "cliente": 1}],
            cliente="cliente")
        assert count == 1
        row = schema.facts["vendas"].get(10)
        assert row is not None
        assert row["cliente_id"] == 1.0
        assert row["valor"] == 100.0

    def test_load_fact_missing_dimension(self) -> None:
        schema = StarSchema("comercial")
        schema.add_dimension("cliente", {"id": "number"})
        schema.add_fact("vendas", {"id": "number"})
        try:
            schema.load_fact("vendas", [{"id": 10, "cliente": 99}],
                             cliente="cliente")
            raised = False
        except WarehouseError:
            raised = True
        assert raised is True

    def test_stats(self) -> None:
        schema = StarSchema("s")
        schema.add_dimension("d", {"id": "number"})
        schema.add_fact("f", {"id": "number"})
        schema.dimensions["d"].insert({"id": 1})
        stats = schema.stats()
        assert stats["dimensions"]["d"] == 1
        assert stats["facts"]["f"] == 0


class TestWarehouseEngine:
    def test_write_and_query(self) -> None:
        engine = make_warehouse()
        engine.create_table("vendas", {"id": "number", "valor": "number"})
        result = engine.write([{"id": 1, "valor": 10.0},
                               {"id": 2, "valor": 20.0}], "vendas")
        assert result["written"] == 2
        assert len(engine.query("vendas")) == 2
        assert engine.count("vendas") == 2

    def test_write_unknown_table(self) -> None:
        engine = make_warehouse()
        try:
            engine.write([], "ghost")
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_fact_table_kind(self) -> None:
        engine = make_warehouse()
        table = engine.create_table("f_vendas",
                                    {"id": "number", "cliente_id": "number",
                                     "valor": "number"},
                                    kind="fact")
        assert isinstance(table, FactTable)
        assert "cliente_id" in table.dimensions

    def test_create_schema_and_stats(self) -> None:
        engine = make_warehouse()
        schema = engine.create_schema("comercial")
        assert schema.name == "comercial"
        engine.create_table("t", {"id": "number"})
        engine.write([{"id": 1}], "t")
        stats = engine.stats()
        assert stats["tables"]["t"] == 1
        assert stats["schemas"] == ["comercial"]


class TestStagingArea:
    def test_stage_commit(self) -> None:
        area = StagingArea()
        assert area.stage("vendas", [{"id": 1}, {"id": 2}]) == 2
        assert area.pending() == {"vendas": 2}
        assert len(area.staged("vendas")) == 2

        class Sink:
            def write(self, records, destination):
                return {"written": len(records)}

        result = area.commit("vendas", Sink())
        assert result == {"written": 2}
        assert area.pending() == {}

    def test_commit_empty_raises(self) -> None:
        area = StagingArea()
        try:
            area.commit("ghost", object())
            raised = False
        except WarehouseError:
            raised = True
        assert raised is True

    def test_flush(self) -> None:
        area = StagingArea()
        area.stage("t", [{"a": 1}])
        assert area.flush("t") == 1
        assert area.pending() == {}


class TestLakeZoneAndCatalog:
    def test_put_get_roundtrip(self) -> None:
        from data_intelligence.lake.base import LakeZone
        zone = LakeZone("raw")
        zone.put("k1", {"v": [1, 2, 3]})
        assert zone.get("k1") == {"v": [1, 2, 3]}
        assert zone.exists("k1")
        assert zone.size() == 1
        assert zone.keys() == ["k1"]
        assert zone.delete("k1") is True
        assert zone.delete("k1") is False

    def test_compressed_roundtrip(self) -> None:
        from data_intelligence.lake.base import LakeZone
        zone = LakeZone("raw")
        zone.put("big", {"data": "x" * 1000}, compress=True)
        entry = zone._objects["big"]["meta"]
        assert entry["compressed"] is True
        assert zone.get("big") == {"data": "x" * 1000}

    def test_catalog(self) -> None:
        catalog = LakeCatalog()
        catalog.add(LakeEntry(key="a", zone="raw", size_bytes=10,
                              partition="2026/01"))
        catalog.add(LakeEntry(key="b", zone="cleansed", size_bytes=20,
                              partition="2026/01"))
        catalog.add(LakeEntry(key="c", zone="curated", size_bytes=30,
                              partition="2026/02"))
        assert len(catalog.search(zone="raw")) == 1
        assert len(catalog.search(partition="2026/01")) == 2
        stats = catalog.stats()
        assert stats["total_objects"] == 3
        assert stats["total_bytes"] == 60
        assert catalog.remove("a") is True
        assert catalog.remove("a") is False


class TestLakePartitioning:
    def test_day_key(self) -> None:
        partitioner = DatePartitioner("day")
        key = partitioner.partition_key(datetime(2026, 1, 5))
        assert key == "2026/01/05"
        assert partitioner.object_key("vendas", "2026-01-05") == \
            "2026/01/05/vendas"

    def test_month_and_year(self) -> None:
        assert DatePartitioner("month").partition_key(
            datetime(2026, 12, 31)) == "2026/12"
        assert DatePartitioner("year").partition_key(
            datetime(2026, 7, 1)) == "2026"

    def test_invalid_granularity(self) -> None:
        try:
            DatePartitioner("hour")
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_invalid_date(self) -> None:
        partitioner = DatePartitioner()
        try:
            partitioner.partition_key(12345)
            raised = False
        except ValueError:
            raised = True
        assert raised is True


class TestLakeEngine:
    def test_store_and_read(self) -> None:
        engine = make_lake()
        meta = engine.store([{"v": 1}, {"v": 2}], zone="raw")
        assert meta["records"] == 2
        assert meta["zone"] == "raw"
        assert meta["partition"] is not None
        data = engine.read(meta["object_id"], "raw")
        assert data == [{"v": 1}, {"v": 2}]

    def test_write_sink_compatible(self) -> None:
        engine = make_lake()
        result = engine.write([{"v": 1}], "cleansed")
        assert result["records"] == 1
        assert result["zone"] == "cleansed"

    def test_partition_store(self) -> None:
        engine = make_lake()
        meta = engine.partition("vendas", "raw", "2026-02-10",
                                [{"v": 1}])
        assert "2026/02/10" in meta["partition"]
        assert engine.catalog.get(
            f"{meta['partition']}/{meta['object_id']}") is not None

    def test_unknown_zone(self) -> None:
        engine = make_lake()
        try:
            engine.zone("nope")
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_stats(self) -> None:
        engine = make_lake()
        engine.store([{"v": 1}], zone="raw")
        stats = engine.stats()
        assert stats["catalog"]["total_objects"] == 1
        assert stats["zones"]["raw"] == 1


class TestCompressor:
    def test_roundtrip_and_ratio(self) -> None:
        records = [{"v": i} for i in range(100)]
        blob = Compressor.dumps(records)
        assert Compressor.loads(blob) == records
        raw = str(records).encode("utf-8")
        assert Compressor.ratio(raw, blob) < 1.0
