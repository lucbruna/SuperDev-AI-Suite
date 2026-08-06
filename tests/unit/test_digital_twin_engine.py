"""Unit tests for the Digital Twin twin_engine package."""
from __future__ import annotations

from typing import cast

import pytest

from modules.digital_twin.config.constants import (
    ENTITY_API,
    ENTITY_MODULE,
    ENTITY_PROJECT,
    REL_DEPENDS_ON,
)
from modules.digital_twin.config.digital_twin_config import DigitalTwinConfig
from modules.digital_twin.core import (
    DigitalTwinContext,
    TwinRegistry,
    TwinRegistryError,
)
from modules.digital_twin.twin_engine import (
    BuildResult,
    MappedEntity,
    SnapshotDiff,
    TwinAnalysis,
    TwinAnalyzer,
    TwinEngine,
    TwinMapper,
    TwinMapperError,
    TwinModel,
    TwinModelRegistry,
    TwinSerializer,
    TwinSnapshot,
    TwinSnapshotter,
    TwinValidator,
    ValidationIssue,
    ValidationReport,
    diff_snapshots,
)


def _context() -> DigitalTwinContext:
    return DigitalTwinContext(
        config=DigitalTwinConfig(),
        registry=TwinRegistry(),
    )


def _sample_model() -> TwinModel:
    model = TwinModel(name="sample")
    model.add_entity({"id": "p1", "type": ENTITY_PROJECT, "name": "Acme", "properties": {}})
    model.add_entity({"id": "m1", "type": ENTITY_MODULE, "name": "core", "properties": {}})
    model.add_entity({"id": "a1", "type": ENTITY_API, "name": "api", "properties": {}})
    model.add_relationship("p1", "m1", REL_DEPENDS_ON)
    model.add_relationship("m1", "a1", "connects")
    return model


class TestTwinMapper:
    def test_map_normalizes_raw_record(self) -> None:
        mapped = TwinMapper().map(
            {"id": "svc-1", "type": ENTITY_API, "name": "Gateway", "port": 8080}
        )
        assert isinstance(mapped, MappedEntity)
        assert mapped.id == "svc-1"
        assert mapped.type == ENTITY_API
        assert mapped.name == "Gateway"
        assert mapped.properties == {"port": 8080}

    def test_map_strips_id_type_name_from_properties(self) -> None:
        mapped = TwinMapper().map({"id": "x", "type": ENTITY_MODULE, "name": "n", "extra": 1})
        assert mapped.properties == {"extra": 1}

    def test_map_requires_id_and_type(self) -> None:
        with pytest.raises(TwinMapperError):
            TwinMapper().map({"id": "x"})
        with pytest.raises(TwinMapperError):
            TwinMapper().map({"type": ENTITY_MODULE})

    def test_map_rejects_unsupported_type(self) -> None:
        with pytest.raises(TwinMapperError):
            TwinMapper().map({"id": "x", "type": "alien"})

    def test_map_many(self) -> None:
        raws: list[dict[str, object]] = [
            {"id": "1", "type": ENTITY_MODULE},
            {"id": "2", "type": ENTITY_API},
        ]
        mapped = TwinMapper().map_many(raws)
        assert [m.id for m in mapped] == ["1", "2"]

    def test_to_dict_round_trip(self) -> None:
        mapped = TwinMapper().map({"id": "1", "type": ENTITY_MODULE, "name": "n"})
        assert mapped.to_dict() == {
            "id": "1",
            "type": ENTITY_MODULE,
            "name": "n",
            "properties": {},
        }


class TestTwinModel:
    def test_add_entity_keys_by_id(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "", "properties": {}})
        model.add_entity({"id": "b", "type": ENTITY_MODULE, "name": "", "properties": {}})
        assert model.entity_ids() == ["a", "b"]
        assert len(model) == 2

    def test_add_entity_overwrites_same_id(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "one", "properties": {}})
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "two", "properties": {}})
        assert len(model) == 1
        assert model.entities["a"]["name"] == "two"

    def test_add_relationship(self) -> None:
        model = TwinModel(name="t")
        model.add_relationship("a", "b", REL_DEPENDS_ON)
        assert model.relationships == [
            {"source": "a", "target": "b", "kind": REL_DEPENDS_ON}
        ]

    def test_to_dict_deep_copies(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "", "properties": {}})
        data = model.to_dict()
        model.entities["a"]["name"] = "changed"
        assert cast(dict, data["entities"])["a"]["name"] == ""


class TestTwinEngine:
    def test_build_maps_and_links(self) -> None:
        engine = TwinEngine()
        result = engine.build(
            _context(),
            name="site",
            raw_entities=[
                {"id": "p1", "type": ENTITY_PROJECT, "name": "Acme"},
                {"id": "m1", "type": ENTITY_MODULE, "name": "core"},
            ],
            relationships=[("p1", "m1", REL_DEPENDS_ON)],
        )
        assert isinstance(result, BuildResult)
        assert result.mapped_count == 2
        assert result.model.name == "site"
        assert result.model.entity_ids() == ["p1", "m1"]
        assert len(result.model.relationships) == 1

    def test_build_records_stats_and_artifact(self) -> None:
        ctx = _context()
        engine = TwinEngine()
        engine.build(
            ctx,
            raw_entities=[{"id": "m1", "type": ENTITY_MODULE, "name": "core"}],
        )
        assert ctx.stats["twin.entities"] == 1
        assert ctx.stats["twin.relationships"] == 0
        assert cast(dict, ctx.get_artifact("twin"))["name"] == "default"

    def test_build_publishes_event(self) -> None:
        ctx = _context()
        seen: list[object] = []
        ctx.events.subscribe("twin.built", lambda e: seen.append(e.payload["name"]))
        TwinEngine().build(ctx, name="evt")
        assert seen == ["evt"]

    def test_build_with_empty_entities(self) -> None:
        result = TwinEngine().build(_context(), raw_entities=[])
        assert result.mapped_count == 0
        assert len(result.model) == 0

    def test_run_delegates_to_build(self) -> None:
        result = TwinEngine().run(_context())
        assert result.model.name == "default"

    def test_to_dict_shape(self) -> None:
        result = TwinEngine().build(
            _context(),
            name="s",
            raw_entities=[{"id": "m1", "type": ENTITY_MODULE, "name": "core"}],
        )
        data = result.to_dict()
        assert data["mapped_count"] == 1
        assert cast(dict, data["twin"])["name"] == "s"


class TestSnapshots:
    def test_from_model_copies_data(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        snap = TwinSnapshot.from_model(model, sequence=1)
        model.entities["a"]["name"] = "changed"
        assert snap.entities["a"]["name"] == "n"
        assert snap.twin_name == "t"
        assert snap.sequence == 1

    def test_snapshotter_monotonic_sequence(self) -> None:
        snapshotter = TwinSnapshotter()
        model = TwinModel(name="t")
        assert snapshotter.capture(model).sequence == 1
        assert snapshotter.capture(model).sequence == 2
        assert snapshotter.sequence == 2

    def test_diff_detects_added(self) -> None:
        before = TwinSnapshot.from_model(TwinModel(name="t"), sequence=1)
        after_model = TwinModel(name="t")
        after_model.add_entity({"id": "new", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        after = TwinSnapshot.from_model(after_model, sequence=2)
        diff = diff_snapshots(before, after)
        assert diff.added == ["new"]
        assert diff.removed == []
        assert diff.changed == []
        assert diff.total == 1
        assert diff.has_changes

    def test_diff_detects_removed(self) -> None:
        before_model = TwinModel(name="t")
        before_model.add_entity({"id": "gone", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        before = TwinSnapshot.from_model(before_model, sequence=1)
        after = TwinSnapshot.from_model(TwinModel(name="t"), sequence=2)
        diff = diff_snapshots(before, after)
        assert diff.removed == ["gone"]

    def test_diff_detects_changed(self) -> None:
        def snap(name: str) -> TwinSnapshot:
            model = TwinModel(name="t")
            model.add_entity(
                {"id": "a", "type": ENTITY_MODULE, "name": name, "properties": {}}
            )
            return TwinSnapshot.from_model(model, sequence=1)

        diff = diff_snapshots(snap("one"), snap("two"))
        assert diff.changed == ["a"]

    def test_diff_no_changes(self) -> None:
        model = TwinModel(name="t")
        before = TwinSnapshot.from_model(model, sequence=1)
        after = TwinSnapshot.from_model(model, sequence=2)
        diff = diff_snapshots(before, after)
        assert not diff.has_changes
        assert diff.to_dict()["total"] == 0


class TestTwinValidator:
    def test_valid_model(self) -> None:
        report = TwinValidator().validate(_sample_model())
        assert report.valid
        assert report.errors == []

    def test_unknown_entity_type_is_error(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "x", "type": "alien", "name": "n", "properties": {}})
        report = TwinValidator().validate(model)
        assert not report.valid
        assert report.errors[0].entity_id == "x"

    def test_missing_name_is_warning(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "x", "type": ENTITY_MODULE, "name": "", "properties": {}})
        report = TwinValidator().validate(model)
        assert report.valid
        assert len(report.issues) == 1
        assert report.issues[0].severity == "warning"

    def test_dangling_relationship_is_error(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        model.add_relationship("a", "missing", REL_DEPENDS_ON)
        report = TwinValidator().validate(model)
        assert not report.valid

    def test_unknown_relation_kind_is_warning(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        model.add_entity({"id": "b", "type": ENTITY_MODULE, "name": "m", "properties": {}})
        model.add_relationship("a", "b", "alien_kind")
        report = TwinValidator().validate(model)
        assert report.valid
        assert any(i.severity == "warning" for i in report.issues)

    def test_report_to_dict(self) -> None:
        report = ValidationReport(
            issues=[ValidationIssue("error", "boom", entity_id="x")]
        )
        data = report.to_dict()
        assert data["valid"] is False
        assert cast(list, data["issues"])[0]["severity"] == "error"


class TestTwinSerializer:
    def test_json_round_trip(self) -> None:
        model = _sample_model()
        restored = TwinSerializer.from_json(TwinSerializer.to_json(model))
        assert restored.to_dict() == model.to_dict()
        assert restored.entity_ids() == ["p1", "m1", "a1"]

    def test_model_from_dict_restores_meta(self) -> None:
        model = _sample_model()
        model.meta = {"source": "manual"}
        restored = TwinSerializer.model_from_dict(model.to_dict())
        assert restored.meta == {"source": "manual"}

    def test_from_json_requires_object(self) -> None:
        with pytest.raises(ValueError):
            TwinSerializer.from_json("[1, 2, 3]")

    def test_snapshot_round_trip(self) -> None:
        model = _sample_model()
        snapshotter = TwinSnapshotter()
        snap = snapshotter.capture(model)
        restored = TwinSerializer.snapshot_from_dict(
            TwinSerializer.snapshot_to_dict(snap), snapshotter
        )
        assert restored.sequence == 2
        assert restored.entities == snap.entities


class TestTwinModelRegistry:
    def test_register_get_has_names(self) -> None:
        registry = TwinModelRegistry()
        registry.register(TwinModel(name="a"))
        registry.register(TwinModel(name="b"))
        assert registry.has("a")
        assert registry.names() == ["a", "b"]
        assert registry.get("a").name == "a"

    def test_duplicate_register_raises(self) -> None:
        registry = TwinModelRegistry()
        registry.register(TwinModel(name="a"))
        with pytest.raises(TwinRegistryError):
            registry.register(TwinModel(name="a"))

    def test_overwrite_allows_reregister(self) -> None:
        registry = TwinModelRegistry()
        registry.register(TwinModel(name="a"))
        registry.register(TwinModel(name="a"), overwrite=True)
        assert len(registry) == 1

    def test_get_missing_raises(self) -> None:
        with pytest.raises(TwinRegistryError):
            TwinModelRegistry().get("nope")

    def test_unregister_and_clear(self) -> None:
        registry = TwinModelRegistry()
        registry.register(TwinModel(name="a"))
        registry.register(TwinModel(name="b"))
        registry.unregister("a")
        assert registry.names() == ["b"]
        registry.clear()
        assert len(registry) == 0

    def test_snapshot_history(self) -> None:
        registry = TwinModelRegistry()
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        registry.register(model)
        registry.snapshot("t")
        registry.snapshot("t")
        assert len(registry.snapshots("t")) == 2
        latest = registry.latest_snapshot("t")
        assert latest is not None
        assert latest.sequence == 2


class TestTwinAnalyzer:
    def test_analyze_counts(self) -> None:
        analysis = TwinAnalyzer().analyze(_sample_model())
        assert isinstance(analysis, TwinAnalysis)
        assert analysis.entity_count == 3
        assert analysis.relationship_count == 2
        assert analysis.types[ENTITY_PROJECT] == 1
        assert analysis.types[ENTITY_MODULE] == 1
        assert analysis.relations[REL_DEPENDS_ON] == 1

    def test_density(self) -> None:
        model = TwinModel(name="t")
        model.add_entity({"id": "a", "type": ENTITY_MODULE, "name": "n", "properties": {}})
        analysis = TwinAnalyzer().analyze(model)
        assert analysis.density == 0.0
        model.add_entity({"id": "b", "type": ENTITY_MODULE, "name": "m", "properties": {}})
        model.add_relationship("a", "b", REL_DEPENDS_ON)
        assert TwinAnalyzer().analyze(model).density == 0.5

    def test_connected_entities(self) -> None:
        analysis = TwinAnalyzer().analyze(_sample_model())
        assert analysis.connected_entities == {"p1", "m1", "a1"}

    def test_to_dict_sorted(self) -> None:
        data = TwinAnalyzer().analyze(_sample_model()).to_dict()
        assert data["entity_count"] == 3
        assert data["connected_entities"] == ["a1", "m1", "p1"]
