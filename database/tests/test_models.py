from __future__ import annotations

import pytest  # type: ignore[import-untyped]

from SuperDev.database.database_models import (
    ConnectionConfig,
    DatabaseConfig,
    DatabaseType,
    MigrationInfo,
    MigrationStatus,
    PoolConfig,
    PoolStrategy,
    QueryResult,
    TransactionInfo,
)


class TestConnectionConfig:
    def test_defaults(self) -> None:
        c = ConnectionConfig()
        assert c.host == "localhost"
        assert c.port == 5432
        assert c.ssl is False
        assert c.timeout == 30.0

    def test_safe_dsn_masks_password(self) -> None:
        c = ConnectionConfig(dsn="postgres://user:secret@localhost/db", password="secret")
        assert "secret" not in c.safe_dsn
        assert "****" in c.safe_dsn

    def test_driver_type_default(self) -> None:
        c = ConnectionConfig()
        assert c.driver_type == DatabaseType.POSTGRESQL

    def test_api_key_field(self) -> None:
        c = ConnectionConfig(api_key="abc123")
        assert c.api_key == "abc123"


class TestDatabaseConfig:
    def test_defaults(self) -> None:
        dc = DatabaseConfig()
        assert dc.default_driver == "postgresql"
        assert dc.enable_metrics is True
        assert dc.slow_query_threshold_ms == 1000.0

    def test_connections_dict(self) -> None:
        dc = DatabaseConfig(connections={"main": ConnectionConfig()})
        assert "main" in dc.connections


class TestPoolConfig:
    def test_defaults(self) -> None:
        pc = PoolConfig()
        assert pc.min_size == 2
        assert pc.max_size == 10
        assert pc.strategy == PoolStrategy.DYNAMIC

    def test_custom_values(self) -> None:
        pc = PoolConfig(min_size=5, max_size=50)
        assert pc.min_size == 5
        assert pc.max_size == 50


class TestQueryResult:
    def test_empty_result(self) -> None:
        qr = QueryResult()
        assert qr.rows == []
        assert qr.row_count == 0
        assert qr.error is None

    def test_with_data(self) -> None:
        qr = QueryResult(rows=[{"id": 1}], row_count=1, duration_ms=5.0)
        assert qr.rows[0]["id"] == 1
        assert qr.duration_ms == 5.0

    def test_error_result(self) -> None:
        qr = QueryResult(error="timeout")
        assert qr.error == "timeout"


class TestMigrationInfo:
    def test_defaults(self) -> None:
        mi = MigrationInfo()
        assert mi.status == MigrationStatus.PENDING
        assert mi.id == ""

    def test_applied_status(self) -> None:
        mi = MigrationInfo(status=MigrationStatus.APPLIED)
        assert mi.status == MigrationStatus.APPLIED


class TestTransactionInfo:
    def test_defaults(self) -> None:
        ti = TransactionInfo()
        assert ti.is_active is True
        assert ti.savepoints == []
        assert len(ti.id) == 32  # uuid4 hex
