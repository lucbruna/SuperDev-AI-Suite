from __future__ import annotations

import pytest

from SuperDev.data.analytics.descriptive import DescriptiveAnalyzer
from SuperDev.data.data_engine import DataEngine
from SuperDev.data.data_models import DataRecord


class TestCentralTendency:
    def test_mean_median(self) -> None:
        analyzer = DescriptiveAnalyzer()
        assert analyzer.mean([1.0, 2.0, 3.0, 4.0]) == 2.5
        assert analyzer.median([1.0, 2.0, 10.0]) == 2.0

    def test_mode_single(self) -> None:
        assert DescriptiveAnalyzer.mode([1.0, 2.0, 2.0, 3.0]) == [2.0]

    def test_mode_empty(self) -> None:
        assert DescriptiveAnalyzer.mode([]) == []

    def test_quantile(self) -> None:
        analyzer = DescriptiveAnalyzer()
        values = [1.0, 2.0, 3.0, 4.0]
        assert analyzer.quantile(values, 0.25) == 1.75
        assert analyzer.quantile(values, 0.5) == 2.5
        assert analyzer.quantile(values, 0.75) == 3.25


class TestDispersion:
    def test_range(self) -> None:
        assert DescriptiveAnalyzer().range([3.0, 1.0, 5.0]) == 4.0

    def test_iqr(self) -> None:
        analyzer = DescriptiveAnalyzer()
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        assert analyzer.iqr(values) == pytest.approx(3.5, abs=1e-3)

    def test_variance_stdev(self) -> None:
        analyzer = DescriptiveAnalyzer()
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        assert analyzer.variance(values) > 0
        assert analyzer.stdev(values) == pytest.approx(analyzer.variance(values) ** 0.5, abs=1e-3)

    def test_stdev_single(self) -> None:
        assert DescriptiveAnalyzer().stdev([5.0]) == 0.0


class TestShape:
    def test_skewness_right(self) -> None:
        analyzer = DescriptiveAnalyzer()
        # right-tailed distribution → positive skew
        skew = analyzer.skewness([1.0, 2.0, 2.0, 3.0, 10.0])
        assert skew > 0

    def test_skewness_symmetric(self) -> None:
        analyzer = DescriptiveAnalyzer()
        skew = analyzer.skewness([1.0, 2.0, 3.0, 4.0, 5.0])
        assert abs(skew) < 0.01

    def test_kurtosis_normal_like(self) -> None:
        analyzer = DescriptiveAnalyzer()
        # small flat series → near-zero excess kurtosis
        assert abs(analyzer.kurtosis([1.0, 2.0, 3.0, 4.0, 5.0])) < 2.0


class TestFrequency:
    def test_histogram(self) -> None:
        analyzer = DescriptiveAnalyzer()
        values = list(range(0, 100, 10))  # 0..90
        dist = analyzer.frequency(values, bins=5)
        assert dist["kind"] == "numeric"
        assert len(dist["bins"]) == 5
        assert sum(b["count"] for b in dist["bins"]) == 10

    def test_histogram_constant(self) -> None:
        dist = DescriptiveAnalyzer().frequency([5.0, 5.0])
        assert dist["bins"][0]["count"] == 2

    def test_histogram_empty(self) -> None:
        dist = DescriptiveAnalyzer().frequency([])
        assert dist["kind"] == "empty"
        assert dist["count"] == 0


class TestRecords:
    def test_extract(self) -> None:
        records = [DataRecord(source="s", data={"v": i}) for i in [1, 2, 3]]
        assert DescriptiveAnalyzer.extract(records, "v") == [1, 2, 3]

    def test_extract_skips_non_numeric(self) -> None:
        records = [
            DataRecord(source="s", data={"v": 1}),
            DataRecord(source="s", data={"v": "x"}),
        ]
        assert DescriptiveAnalyzer.extract(records, "v") == [1]

    def test_describe_records(self) -> None:
        records = [DataRecord(source="s", data={"v": i}) for i in range(1, 11)]
        summary = DescriptiveAnalyzer().describe_records(records, "v")
        assert summary["count"] == 10
        assert summary["mean"] == pytest.approx(5.5)


class TestSummarize:
    def test_full_summary(self) -> None:
        analyzer = DescriptiveAnalyzer()
        summary = analyzer.summarize([1.0, 2.0, 3.0, 4.0], name="x")
        for key in ["count", "mean", "median", "min", "max", "range",
                    "stdev", "variance", "q1", "q3", "iqr", "skewness",
                    "kurtosis", "sum"]:
            assert key in summary
        assert summary["count"] == 4
        assert summary["sum"] == 10.0

    def test_summarize_empty(self) -> None:
        summary = DescriptiveAnalyzer().summarize([], name="e")
        assert summary["count"] == 0
        assert summary["mean"] == 0.0

    def test_history(self) -> None:
        analyzer = DescriptiveAnalyzer()
        analyzer.summarize([1.0, 2.0])
        analyzer.summarize([3.0, 4.0])
        assert len(analyzer.history()) == 2

    def test_summarize_with_engine(self, engine: DataEngine) -> None:
        analyzer = DescriptiveAnalyzer(engine=engine)
        analyzer.summarize([1.0, 2.0], name="field-a")
        assert engine.metrics.get_counter("analytics.descriptive_runs", {"field": "field-a"}) >= 1
