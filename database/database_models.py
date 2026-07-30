from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    CLICKHOUSE = "clickhouse"
    CASSANDRA = "cassandra"
    NEO4J = "neo4j"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"


class IsolationLevel(str, Enum):
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"
    SNAPSHOT = "snapshot"


class MigrationStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class PoolStrategy(str, Enum):
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    THREADED = "threaded"


class ConnectionState(str, Enum):
    CLOSED = "closed"
    CONNECTING = "connecting"
    OPEN = "open"
    CLOSING = "closing"
    ERROR = "error"


@dataclass
class ConnectionConfig:
    dsn: str = ""
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""
    timeout: float = 30.0
    ssl: bool = False
    api_key: str = ""
    options: dict[str, Any] = field(default_factory=dict)
    driver_type: DatabaseType = DatabaseType.POSTGRESQL
    pool_config: PoolConfig | None = None

    @property
    def safe_dsn(self) -> str:
        masked = self.dsn
        if self.password and self.password in masked:
            masked = masked.replace(self.password, "****")
        return masked


@dataclass
class PoolConfig:
    min_size: int = 2
    max_size: int = 10
    strategy: PoolStrategy = PoolStrategy.DYNAMIC
    acquire_timeout: float = 30.0
    max_idle_time: float = 300.0
    max_lifetime: float = 3600.0
    validation_query: str = "SELECT 1"


@dataclass
class DatabaseConfig:
    default_driver: str = "postgresql"
    connections: dict[str, ConnectionConfig] = field(default_factory=dict)
    pools: dict[str, PoolConfig] = field(default_factory=dict)
    migrations_dir: str = "migrations"
    enable_metrics: bool = True
    enable_health: bool = True
    log_queries: bool = False
    slow_query_threshold_ms: float = 1000.0


@dataclass
class QueryResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    columns: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    error: str | None = None
    last_insert_id: Any = None


@dataclass
class TransactionInfo:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    started_at: float = field(default_factory=time.time)
    savepoints: list[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class MigrationInfo:
    id: str = ""
    name: str = ""
    version: str = ""
    status: MigrationStatus = MigrationStatus.PENDING
    executed_at: float | None = None
    duration_ms: float = 0.0
    checksum: str = ""
    sql_up: str = ""
    sql_down: str = ""


@dataclass
class ColumnMetadata:
    name: str = ""
    data_type: str = ""
    nullable: bool = True
    is_pk: bool = False
    is_unique: bool = False
    default: Any = None
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None
    foreign_key: str | None = None


@dataclass
class IndexMetadata:
    name: str = ""
    columns: list[str] = field(default_factory=list)
    is_unique: bool = False
    is_primary: bool = False
    method: str = "btree"


@dataclass
class EntityMetadata:
    table: str = ""
    schema: str = "public"
    columns: list[ColumnMetadata] = field(default_factory=list)
    indexes: list[IndexMetadata] = field(default_factory=list)
    primary_key: str = "id"
    relationships: dict[str, str] = field(default_factory=dict)


@dataclass
class ShardKey:
    column: str = ""
    value: Any = None
    strategy: str = "hash"


@dataclass
class ReplicaInfo:
    name: str = ""
    host: str = ""
    port: int = 5432
    is_primary: bool = False
    lag_bytes: int = 0
    is_healthy: bool = True


@dataclass
class PoolStatus:
    active: int = 0
    idle: int = 0
    waiting: int = 0
    total: int = 0
    max: int = 10
    min: int = 2


@dataclass
class QueryProfile:
    query: str = ""
    duration_ms: float = 0.0
    rows_affected: int = 0
    timestamp: float = field(default_factory=time.time)
    driver: str = ""
    success: bool = True
    error: str | None = None
