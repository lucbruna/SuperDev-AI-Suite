from __future__ import annotations

import pytest  # type: ignore[import-untyped]

from SuperDev.database.monitoring import DatabaseHealthChecker, DatabaseMetricsCollector


class TestDatabaseMetricsCollector:
    @pytest.fixture()
    def metrics(self) -> DatabaseMetricsCollector:
        return DatabaseMetricsCollector()

    def test_record_query(self, metrics: DatabaseMetricsCollector) -> None:
        metrics.record_query(5.0, "sqlite", True)
        m = metrics.get_metrics()
        assert m["total_queries"] == 1
        assert m["error_count"] == 0

    def test_record_errors(self, metrics: DatabaseMetricsCollector) -> None:
        metrics.record_query(10.0, "pg", False)
        m = metrics.get_metrics()
        assert m["error_count"] == 1

    def test_average_duration(self, metrics: DatabaseMetricsCollector) -> None:
        metrics.record_query(5.0, "pg", True)
        metrics.record_query(15.0, "pg", True)
        m = metrics.get_metrics()
        assert m["avg_duration_ms"] == 10.0

    def test_connections(self, metrics: DatabaseMetricsCollector) -> None:
        metrics.record_connection("pg")
        metrics.record_connection("pg")
        metrics.record_disconnection("pg")
        m = metrics.get_metrics()
        assert m["connections"]["pg"] == 1

    def test_pool_stats(self, metrics: DatabaseMetricsCollector) -> None:
        metrics.record_pool_stats("pg", active=3, idle=2, waiting=0)
        m = metrics.get_metrics()
        assert m["pool_stats"]["pg"]["active"] == 3
        assert m["pool_stats"]["pg"]["total"] == 5

    def test_initial_state(self, metrics: DatabaseMetricsCollector) -> None:
        m = metrics.get_metrics()
        assert m["total_queries"] == 0
        assert m["error_count"] == 0
        assert m["avg_duration_ms"] == 0.0

    def test_reset(self, metrics: DatabaseMetricsCollector) -> None:
        metrics.record_query(5.0, "pg", True)
        metrics.reset()
        m = metrics.get_metrics()
        assert m["total_queries"] == 0

    def test_max_queries(self, metrics: DatabaseMetricsCollector) -> None:
        for i in range(12_000):
            metrics.record_query(1.0, "pg", True)
        m = metrics.get_metrics()
        # Should have trimmed to 5_000 + remainder after trim
        assert m["total_queries"] < 12_000  # was trimmed


class TestDatabaseHealthChecker:
    @pytest.fixture()
    def checker(self) -> DatabaseHealthChecker:
        return DatabaseHealthChecker()

    def test_check_no_drivers(self, checker: DatabaseHealthChecker) -> None:
        import asyncio

        result = asyncio.run(checker.check())
        assert result["status"] == "healthy"
        assert result["drivers"] == {}

    def test_check_unknown_driver(self, checker: DatabaseHealthChecker) -> None:
        import asyncio

        result = asyncio.run(checker.check_driver("missing"))
        assert result["healthy"] is False
        assert "not found" in result["error"]
