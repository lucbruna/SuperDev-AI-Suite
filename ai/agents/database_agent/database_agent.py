from __future__ import annotations

from typing import Any

from .backup import Backup
from .consistency import Consistency
from .index_optimizer import IndexOptimizer
from .migration_generator import MigrationGenerator
from .partitioning import Partitioning
from .query_optimizer import QueryOptimizer
from .replication import Replication
from .restore import Restore
from .schema_designer import SchemaDesigner
from .sharding import Sharding


class DatabaseAgent:
    """Central orchestrator for database design and management."""

    def __init__(self) -> None:
        self._schema = SchemaDesigner()
        self._migrations = MigrationGenerator()
        self._query_opt = QueryOptimizer()
        self._index_opt = IndexOptimizer()
        self._replication = Replication()
        self._backup = Backup()
        self._restore = Restore()
        self._consistency = Consistency()
        self._partitioning = Partitioning()
        self._sharding = Sharding()

    @property
    def schema(self) -> SchemaDesigner:
        return self._schema

    @property
    def migrations(self) -> MigrationGenerator:
        return self._migrations

    @property
    def query_optimizer(self) -> QueryOptimizer:
        return self._query_opt

    @property
    def index_optimizer(self) -> IndexOptimizer:
        return self._index_opt

    @property
    def replication(self) -> Replication:
        return self._replication

    @property
    def backup(self) -> Backup:
        return self._backup

    @property
    def restore(self) -> Restore:
        return self._restore

    @property
    def consistency(self) -> Consistency:
        return self._consistency

    @property
    def partitioning(self) -> Partitioning:
        return self._partitioning

    @property
    def sharding(self) -> Sharding:
        return self._sharding

    def design_database(self, spec: dict[str, Any]) -> dict[str, Any]:
        tables = spec.get("tables", [])
        for t in tables:
            self._schema.add_table(t.get("name", "table"), t.get("columns", []))
        return {
            "status": "designed",
            "tables": self._schema.table_count,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "tables": self._schema.table_count,
            "migrations": self._migrations.migration_count,
            "queries": self._query_opt.query_count,
            "indexes": self._index_opt.index_count,
            "replicas": self._replication.replica_count,
            "shards": self._sharding.shard_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "database_agent", "status": self.get_status()}
