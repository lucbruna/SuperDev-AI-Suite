from __future__ import annotations

from ..backup import Backup
from ..consistency import Consistency
from ..database_agent import DatabaseAgent
from ..index_optimizer import IndexOptimizer
from ..migration_generator import MigrationGenerator
from ..partitioning import Partitioning
from ..query_optimizer import QueryOptimizer
from ..replication import Replication
from ..restore import Restore
from ..schema_designer import SchemaDesigner
from ..sharding import Sharding


class TestSchemaDesigner:
    def test_add_table(self) -> None:
        sd = SchemaDesigner()
        sd.add_table("users", [{"name": "id", "type": "INT"}])
        assert sd.table_count == 1

    def test_get_table(self) -> None:
        sd = SchemaDesigner()
        sd.add_table("users", [])
        assert sd.get_table("users") is not None

    def test_foreign_key(self) -> None:
        sd = SchemaDesigner()
        sd.add_table("orders", [])
        assert sd.add_foreign_key("orders", "user_id", "users", "id") is True

    def test_generate_ddl(self) -> None:
        sd = SchemaDesigner()
        sd.add_table("users", [{"name": "id", "type": "INT"}])
        ddl = sd.generate_ddl("users")
        assert "CREATE TABLE" in ddl

    def test_to_dict(self) -> None:
        sd = SchemaDesigner()
        sd.add_table("t", [])
        assert "tables" in sd.to_dict()


class TestMigrationGenerator:
    def test_create_migration(self) -> None:
        mg = MigrationGenerator()
        mid = mg.create_migration("add_users", "CREATE TABLE", "DROP TABLE")
        assert mid.startswith("mig_")

    def test_apply(self) -> None:
        mg = MigrationGenerator()
        mg.create_migration("m1", "UP", "DOWN")
        applied = mg.apply_migrations()
        assert len(applied) == 1

    def test_rollback(self) -> None:
        mg = MigrationGenerator()
        mg.create_migration("m1", "UP", "DOWN")
        mg.apply_migrations()
        rolled = mg.rollback_migrations(1)
        assert len(rolled) == 1

    def test_pending_count(self) -> None:
        mg = MigrationGenerator()
        mg.create_migration("m1", "UP", "DOWN")
        assert mg.pending_count == 1

    def test_to_dict(self) -> None:
        mg = MigrationGenerator()
        mg.create_migration("m", "U", "D")
        assert "migrations" in mg.to_dict()


class TestQueryOptimizer:
    def test_add_query(self) -> None:
        qo = QueryOptimizer()
        qo.add_query("q1", "SELECT * FROM users")
        assert qo.query_count == 1

    def test_analyze_query(self) -> None:
        qo = QueryOptimizer()
        results = qo.analyze_query("SELECT * FROM users")
        assert len(results) > 0

    def test_suggest_indexes(self) -> None:
        qo = QueryOptimizer()
        indexes = qo.suggest_indexes("SELECT * FROM users WHERE email = 'a'")
        assert len(indexes) > 0

    def test_to_dict(self) -> None:
        qo = QueryOptimizer()
        qo.add_query("q", "SELECT 1")
        assert "queries" in qo.to_dict()


class TestIndexOptimizer:
    def test_add_index(self) -> None:
        io = IndexOptimizer()
        io.add_index("idx_email", "users", ["email"])
        assert io.index_count == 1

    def test_list_by_table(self) -> None:
        io = IndexOptimizer()
        io.add_index("i1", "users", ["email"])
        io.add_index("i2", "orders", ["id"])
        assert len(io.list_indexes("users")) == 1

    def test_to_dict(self) -> None:
        io = IndexOptimizer()
        io.add_index("i", "t", ["c"])
        assert "indexes" in io.to_dict()


class TestReplication:
    def test_configure(self) -> None:
        r = Replication()
        r.configure("sync")
        assert r.replication_mode == "sync"

    def test_add_replica(self) -> None:
        r = Replication()
        r.add_replica("replica1")
        assert r.replica_count == 1

    def test_get_status(self) -> None:
        r = Replication()
        s = r.get_status()
        assert "mode" in s

    def test_to_dict(self) -> None:
        r = Replication()
        r.add_replica("r1")
        assert "replicas" in r.to_dict()


class TestBackup:
    def test_create_backup(self) -> None:
        b = Backup()
        bid = b.create_backup("nightly")
        assert bid.startswith("bkp_")

    def test_list_backups(self) -> None:
        b = Backup()
        b.create_backup("b1")
        assert len(b.list_backups()) == 1

    def test_schedule(self) -> None:
        b = Backup()
        b.schedule_backup("0 0 * * *")
        assert b.scheduled_count == 1

    def test_to_dict(self) -> None:
        b = Backup()
        b.create_backup("b")
        d = b.to_dict()
        assert "backups" in d


class TestRestore:
    def test_restore(self) -> None:
        r = Restore()
        rid = r.restore_from_backup("bkp_0001")
        assert rid.startswith("rst_")

    def test_dry_run(self) -> None:
        r = Restore()
        result = r.dry_run("bkp_0001")
        assert "will_restore" in result

    def test_validate(self) -> None:
        r = Restore()
        assert r.validate_backup("bkp_0001") is True
        assert r.validate_backup("invalid") is False

    def test_to_dict(self) -> None:
        r = Restore()
        r.restore_from_backup("bkp_1")
        assert "restores" in r.to_dict()


class TestConsistency:
    def test_add_check(self) -> None:
        c = Consistency()
        c.add_check("row_count", "SELECT COUNT(*)", "100")
        assert c.check_count == 1

    def test_run_checks(self) -> None:
        c = Consistency()
        c.add_check("c1", "SELECT 1", "1")
        results = c.run_checks()
        assert len(results) == 1

    def test_to_dict(self) -> None:
        c = Consistency()
        c.add_check("c", "SELECT 1", "1")
        assert "checks" in c.to_dict()


class TestPartitioning:
    def test_add_strategy(self) -> None:
        p = Partitioning()
        p.add_strategy("orders", "range", "created_at")
        assert p.strategy_count == 1

    def test_generate_sql(self) -> None:
        p = Partitioning()
        p.add_strategy("orders", "hash", "id")
        sql = p.generate_partition_sql("orders")
        assert "PARTITION BY" in sql

    def test_to_dict(self) -> None:
        p = Partitioning()
        p.add_strategy("t", "range", "c")
        assert "strategies" in p.to_dict()


class TestSharding:
    def test_add_shard(self) -> None:
        s = Sharding()
        s.add_shard("shard1", "host1")
        assert s.shard_count == 1

    def test_distribute(self) -> None:
        s = Sharding()
        s.add_shard("s1", "h1")
        s.add_shard("s2", "h2")
        mapping = s.distribute_data(["a", "b", "c"])
        assert len(mapping) == 3

    def test_rebalance(self) -> None:
        s = Sharding()
        s.add_shard("s1", "h1")
        s.add_shard("s2", "h2")
        s.distribute_data(["a", "b", "c", "d"])
        result = s.rebalance()
        assert "status" in result

    def test_to_dict(self) -> None:
        s = Sharding()
        s.add_shard("s1", "h1")
        assert "shards" in s.to_dict()


class TestDatabaseAgent:
    def test_engine_initializes(self) -> None:
        da = DatabaseAgent()
        assert da.schema is not None
        assert da.migrations is not None
        assert da.query_optimizer is not None
        assert da.index_optimizer is not None
        assert da.replication is not None
        assert da.backup is not None
        assert da.restore is not None
        assert da.consistency is not None
        assert da.partitioning is not None
        assert da.sharding is not None

    def test_design_database(self) -> None:
        da = DatabaseAgent()
        result = da.design_database({"tables": [{"name": "users", "columns": [{"name": "id", "type": "INT"}]}]})
        assert result["status"] == "designed"

    def test_get_status(self) -> None:
        da = DatabaseAgent()
        s = da.get_status()
        assert "tables" in s

    def test_to_dict(self) -> None:
        da = DatabaseAgent()
        d = da.to_dict()
        assert d["agent"] == "database_agent"
