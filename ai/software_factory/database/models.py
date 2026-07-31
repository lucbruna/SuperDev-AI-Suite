"""Data models for database management."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ColumnType(Enum):
    INTEGER = "integer"
    BIGINT = "bigint"
    FLOAT = "float"
    DOUBLE = "double"
    DECIMAL = "decimal"
    VARCHAR = "varchar"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    BLOB = "blob"
    JSON = "json"
    UUID = "uuid"


class MigrationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Column:
    """A column in a database table."""
    name: str = ""
    column_type: ColumnType = ColumnType.VARCHAR
    nullable: bool = True
    default_value: Any = None
    primary_key: bool = False
    auto_increment: bool = False
    unique: bool = False
    max_length: int | None = None
    description: str = ""


@dataclass
class Index:
    """A database index."""
    index_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    columns: list[str] = field(default_factory=list)
    unique: bool = False
    table_name: str = ""


@dataclass
class ForeignKey:
    """A foreign key constraint."""
    name: str = ""
    columns: list[str] = field(default_factory=list)
    reference_table: str = ""
    reference_columns: list[str] = field(default_factory=list)
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"


@dataclass
class Table:
    """A database table."""
    table_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    columns: list[Column] = field(default_factory=list)
    indexes: list[Index] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    description: str = ""

    def add_column(self, column: Column) -> None:
        self.columns.append(column)

    def get_column(self, name: str) -> Column | None:
        for c in self.columns:
            if c.name == name:
                return c
        return None

    def primary_key_columns(self) -> list[Column]:
        return [c for c in self.columns if c.primary_key]

    def has_column(self, name: str) -> bool:
        return any(c.name == name for c in self.columns)


@dataclass
class DatabaseSchema:
    """A complete database schema."""
    schema_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    version: str = "1.0.0"
    tables: list[Table] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_table(self, table: Table) -> None:
        self.tables.append(table)

    def get_table(self, name: str) -> Table | None:
        for t in self.tables:
            if t.name == name:
                return t
        return None

    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]

    def total_columns(self) -> int:
        return sum(len(t.columns) for t in self.tables)


@dataclass
class MigrationStep:
    """A single step in a migration."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    operation: str = ""
    table_name: str = ""
    sql: str = ""
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Migration:
    """A database migration."""
    migration_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    steps: list[MigrationStep] = field(default_factory=list)
    status: MigrationStatus = MigrationStatus.PENDING
    version: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: datetime | None = None


@dataclass
class DatabaseConnection:
    """Database connection configuration."""
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    engine: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""
    options: dict[str, Any] = field(default_factory=dict)

    def connection_string(self) -> str:
        return f"{self.engine}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
