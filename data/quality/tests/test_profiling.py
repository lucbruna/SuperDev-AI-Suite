from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine
from SuperDev.data.data_models import DataRecord
from SuperDev.data.quality.profiling import DataProfiler


def _records(rows: list[dict]) -> list[DataRecord]:
    return [DataRecord(source="prof", data=dict(row)) for row in rows]


class TestTypeInference:
    def test_numeric(self) -> None:
        assert DataProfiler.infer_type([1, 2, 3]) == "numeric"

    def test_boolean(self) -> None:
        assert DataProfiler.infer_type([True, False, True]) == "boolean"

    def test_text(self) -> None:
        assert DataProfiler.infer_type(["a", "b", "c"]) == "text"

    def test_mixed(self) -> None:
        assert DataProfiler.infer_type([1, "a", None]) == "mixed"

    def test_empty(self) -> None:
        assert DataProfiler.infer_type([None, "", None]) == "empty"


class TestFieldProfile:
    def test_numeric_field(self) -> None:
        records = _records([{"value": v} for v in [1, 2, 3, 4]])
        profile = DataProfiler().profile_field(records, "value")
        assert profile["type"] == "numeric"
        assert profile["min"] == 1
        assert profile["max"] == 4
        assert profile["mean"] == 2.5
        assert profile["nulls"] == 0

    def test_field_with_nulls(self) -> None:
        records = _records([{"v": 1}, {"v": None}, {"v": 3}])
        profile = DataProfiler().profile_field(records, "v")
        assert profile["nulls"] == 1
        # null_rate is rounded to 4 decimals
        assert profile["null_rate"] == pytest.approx(1 / 3, abs=1e-3)

    def test_categorical_top_values(self) -> None:
        records = _records([{"region": r} for r in ["US", "US", "EU", "US", "EU", "ASIA"]])
        profile = DataProfiler().profile_field(records, "region")
        assert profile["type"] == "text"
        assert profile["top_values"][0]["value"] == "US"


class TestDatasetProfile:
    def test_full_profile(self) -> None:
        records = _records([{"id": i, "value": i * 2} for i in range(10)])
        report = DataProfiler().profile(records, "asset-1")
        assert report["records"] == 10
        assert report["duplicate_rate"] == 0.0
        assert report["overall_null_rate"] == 0.0
        assert "id" in report["fields"] and "value" in report["fields"]

    def test_duplicate_detection(self) -> None:
        records = _records([{"id": 1}, {"id": 1}, {"id": 2}])
        report = DataProfiler().profile(records, "dup")
        # duplicate_rate is rounded to 4 decimals
        assert report["duplicate_rate"] == pytest.approx(1 / 3, abs=1e-3)

    def test_empty_dataset(self) -> None:
        report = DataProfiler().profile([], "empty-asset")
        assert report["records"] == 0
        assert report["fields"] == []

    def test_get_profile_cached(self) -> None:
        profiler = DataProfiler()
        profiler.profile(_records([{"a": 1}]), "cached")
        assert profiler.get_profile("cached") is not None
        assert profiler.get_profile("missing") is None

    def test_profile_with_engine(self, engine: DataEngine) -> None:
        profiler = DataProfiler(engine=engine)
        profiler.profile(_records([{"a": 1}]), "asset-engine")
        assert engine.metrics.get_counter("quality.profiling_runs", {"asset": "asset-engine"}) >= 1


class TestDistribution:
    def test_numeric_histogram(self) -> None:
        records = _records([{"v": v} for v in range(0, 100, 10)])
        dist = DataProfiler().distribution(records, "v", bins=5)
        assert dist["kind"] == "numeric"
        assert len(dist["bins"]) == 5
        assert sum(b["count"] for b in dist["bins"]) == 10

    def test_categorical_frequency(self) -> None:
        records = _records([{"tag": t} for t in ["a", "a", "b"]])
        dist = DataProfiler().distribution(records, "tag")
        assert dist["kind"] == "categorical"
        assert dist["top_values"][0] == {"value": "a", "count": 2}

    def test_constant_numeric(self) -> None:
        records = _records([{"v": 5}, {"v": 5}])
        dist = DataProfiler().distribution(records, "v")
        assert dist["bins"][0]["count"] == 2


class TestDrift:
    def test_no_drift(self) -> None:
        profiler = DataProfiler()
        baseline = profiler.profile(_records([{"v": v} for v in range(10)]), "b")
        current = profiler.profile(_records([{"v": v} for v in range(10)]), "c")
        assert profiler.drift_score(baseline, current) == 0.0

    def test_high_drift(self) -> None:
        profiler = DataProfiler()
        baseline = profiler.profile(_records([{"v": v} for v in range(10)]), "b")
        current = profiler.profile(_records([{"v": v} for v in range(1000, 1010)]), "c")
        score = profiler.drift_score(baseline, current)
        assert score > 0.9

    def test_drift_no_shared_fields(self) -> None:
        profiler = DataProfiler()
        baseline = profiler.profile(_records([{"v": 1}]), "b")
        current = profiler.profile(_records([{"w": 1}]), "c")
        assert profiler.drift_score(baseline, current) == 0.0
