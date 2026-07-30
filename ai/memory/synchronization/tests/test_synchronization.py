from __future__ import annotations

from ..synchronization_engine import SynchronizationEngine
from ..replication import Replication
from ..distributed_memory import DistributedMemory
from ..node_sync import NodeSync
from ..cluster_sync import ClusterSync
from ..transaction_manager import TransactionManager
from ..conflict_resolution import ConflictResolution
from ..consistency_checker import ConsistencyChecker


class TestSynchronizationEngine:
    def setup_method(self) -> None:
        self.engine = SynchronizationEngine()

    def test_synchronize(self) -> None:
        local = {"a": 1, "b": 2}
        remote = {"b": 3, "c": 4}
        result = self.engine.synchronize(local, remote)
        assert "merged" in result
        assert "conflicts_resolved" in result
        assert result["merged"]["a"] == 1

    def test_snapshot(self) -> None:
        snap = self.engine.snapshot()
        assert "sync_count" in snap

    def test_properties(self) -> None:
        assert isinstance(self.engine.replication, Replication)
        assert isinstance(self.engine.distributed, DistributedMemory)
        assert isinstance(self.engine.node_sync, NodeSync)
        assert isinstance(self.engine.cluster_sync, ClusterSync)
        assert isinstance(self.engine.transactions, TransactionManager)
        assert isinstance(self.engine.conflicts, ConflictResolution)
        assert isinstance(self.engine.consistency, ConsistencyChecker)


class TestReplication:
    def setup_method(self) -> None:
        self.rep = Replication()

    def test_replicate_and_get(self) -> None:
        self.rep.replicate({"key": "val"}, "node1")
        assert self.rep.get_replica("node1") == {"key": "val"}
        assert self.rep.get_replica("nonexistent") is None

    def test_merge(self) -> None:
        merged = self.rep.merge({"a": 1}, {"b": 2})
        assert merged == {"a": 1, "b": 2}

    def test_merge_overlap(self) -> None:
        merged = self.rep.merge({"a": {"x": 1}}, {"a": {"y": 2}})
        assert merged["a"] == {"x": 1, "y": 2}

    def test_list_targets(self) -> None:
        self.rep.replicate({}, "n1")
        self.rep.replicate({}, "n2")
        assert set(self.rep.list_targets()) == {"n1", "n2"}

    def test_remove_replica(self) -> None:
        self.rep.replicate({}, "n")
        assert self.rep.remove_replica("n") is True
        assert self.rep.remove_replica("n") is False

    def test_replication_count(self) -> None:
        self.rep.replicate({}, "a")
        self.rep.replicate({}, "b")
        self.rep.merge({}, {})
        assert self.rep.replication_count == 3


class TestDistributedMemory:
    def setup_method(self) -> None:
        self.dm = DistributedMemory()

    def test_register_and_list_nodes(self) -> None:
        self.dm.register_node("n1", {"region": "us"})
        assert "n1" in self.dm.list_nodes()
        assert self.dm.node_count == 1

    def test_unregister_node(self) -> None:
        self.dm.register_node("n1")
        assert self.dm.unregister_node("n1") is True
        assert self.dm.unregister_node("n1") is False

    def test_partitions(self) -> None:
        self.dm.assign_partition("p1", ["n1", "n2"])
        assert self.dm.get_partition("p1") == ["n1", "n2"]
        assert self.dm.get_node_partitions("n1") == ["p1"]

    def test_distribute(self) -> None:
        self.dm.register_node("n1")
        self.dm.register_node("n2")
        mapping = self.dm.distribute({"a": 1, "b": 2, "c": 3})
        assert len(mapping) >= 1

    def test_distribute_no_nodes(self) -> None:
        assert self.dm.distribute({"a": 1}) == {}

    def test_clear(self) -> None:
        self.dm.register_node("n1")
        self.dm.clear()
        assert self.dm.node_count == 0


class TestNodeSync:
    def setup_method(self) -> None:
        self.ns = NodeSync()

    def test_register_and_list(self) -> None:
        self.ns.register("n1")
        assert "n1" in self.ns.list_nodes()

    def test_unregister(self) -> None:
        self.ns.register("n")
        assert self.ns.unregister("n") is True
        assert self.ns.unregister("n") is False

    def test_record_sync(self) -> None:
        self.ns.register("a")
        self.ns.register("b")
        self.ns.record_sync("a", "b")
        assert self.ns.last_sync("a") is not None

    def test_sync_status(self) -> None:
        self.ns.register("n")
        assert self.ns.sync_status("n") == "active"
        assert self.ns.sync_status("unknown") is None

    def test_sync_history(self) -> None:
        self.ns.register("a")
        self.ns.register("b")
        self.ns.record_sync("a", "b")
        history = self.ns.get_sync_history()
        assert len(history) == 1

    def test_clear(self) -> None:
        self.ns.register("n")
        self.ns.clear()
        assert self.ns.node_count == 0


class TestClusterSync:
    def setup_method(self) -> None:
        self.cs = ClusterSync()

    def test_register_and_list(self) -> None:
        self.cs.register_cluster("c1", ["n1", "n2"])
        assert "c1" in self.cs.list_clusters()
        assert self.cs.cluster_count == 1

    def test_unregister(self) -> None:
        self.cs.register_cluster("c")
        assert self.cs.unregister_cluster("c") is True
        assert self.cs.unregister_cluster("c") is False

    def test_add_remove_node(self) -> None:
        self.cs.register_cluster("c")
        assert self.cs.add_node("c", "n1") is True
        assert self.cs.add_node("nonexistent", "n1") is False
        assert self.cs.remove_node("c", "n1") is True
        assert self.cs.remove_node("c", "n1") is False

    def test_sync_cluster(self) -> None:
        self.cs.register_cluster("c", ["n1"])
        result = self.cs.sync_cluster("c")
        assert result["node_count"] == 1
        assert self.cs.sync_cluster("nonexistent")["error"] == "cluster not found"

    def test_cluster_info(self) -> None:
        self.cs.register_cluster("c")
        info = self.cs.cluster_info("c")
        assert info is not None
        assert self.cs.cluster_info("unknown") is None

    def test_clear(self) -> None:
        self.cs.register_cluster("c")
        self.cs.clear()
        assert self.cs.cluster_count == 0


class TestTransactionManager:
    def setup_method(self) -> None:
        self.tm = TransactionManager()

    def test_begin_and_commit(self) -> None:
        tx = self.tm.begin([{"op": "write", "key": "a"}])
        assert tx.status == "pending"
        assert self.tm.commit(tx.transaction_id) is True
        assert tx.status == "committed"

    def test_rollback(self) -> None:
        tx = self.tm.begin([])
        assert self.tm.rollback(tx.transaction_id) is True
        assert tx.status == "rolled_back"

    def test_commit_nonexistent(self) -> None:
        assert self.tm.commit("nonexistent") is False

    def test_list_active(self) -> None:
        self.tm.begin([])
        self.tm.begin([])
        assert len(self.tm.list_active()) == 2

    def test_get_transaction(self) -> None:
        tx = self.tm.begin([])
        assert self.tm.get_transaction(tx.transaction_id) is tx
        assert self.tm.get_transaction("nonexistent") is None

    def test_active_count(self) -> None:
        self.tm.begin([])
        assert self.tm.active_count == 1
        tx = self.tm.begin([])
        self.tm.commit(tx.transaction_id)
        assert self.tm.active_count == 1

    def test_clear(self) -> None:
        self.tm.begin([])
        self.tm.clear()
        assert self.tm.active_count == 0


class TestConflictResolution:
    def setup_method(self) -> None:
        self.cr = ConflictResolution()

    def test_detect(self) -> None:
        conflicts = self.cr.detect({"a": 1, "b": 2}, {"a": 1, "b": 3})
        assert len(conflicts) == 1
        assert conflicts[0]["key"] == "b"

    def test_detect_no_conflicts(self) -> None:
        conflicts = self.cr.detect({"a": 1}, {"a": 1})
        assert len(conflicts) == 0

    def test_resolve_local(self) -> None:
        data = {"a": 1, "b": 2}
        conflicts = [{"key": "b", "local_value": 2, "remote_value": 3}]
        resolved = self.cr.resolve(data, conflicts, "local")
        assert resolved["b"] == 2

    def test_resolve_remote(self) -> None:
        data = {"a": 1, "b": 2}
        conflicts = [{"key": "b", "local_value": 2, "remote_value": 3}]
        resolved = self.cr.resolve(data, conflicts, "remote")
        assert resolved["b"] == 3

    def test_resolve_all(self) -> None:
        resolved = self.cr.resolve_all({"a": 1}, {"a": 2}, "remote")
        assert resolved["a"] == 2

    def test_stats(self) -> None:
        self.cr.resolve({}, [{"key": "a", "local_value": 1, "remote_value": 2}])
        assert self.cr.stats()["conflicts_resolved"] == 1

    def test_clear(self) -> None:
        self.cr.resolve({}, [{"key": "a", "local_value": 1, "remote_value": 2}])
        self.cr.clear()
        assert self.cr.conflicts_resolved == 0


class TestConsistencyChecker:
    def setup_method(self) -> None:
        self.checker = ConsistencyChecker()

    def test_check(self) -> None:
        assert self.checker.check({"a": 1}) is True
        assert self.checker.check("not_dict") is False

    def test_compare_consistent(self) -> None:
        result = self.checker.compare({"a": 1}, {"a": 1})
        assert result["consistent"] is True
        assert result["matching"] == 1

    def test_compare_diverging(self) -> None:
        result = self.checker.compare({"a": 1}, {"a": 2})
        assert result["consistent"] is False
        assert result["diverging"] == 1

    def test_compare_missing(self) -> None:
        result = self.checker.compare({"a": 1}, {"b": 2})
        assert result["missing_local"] == 1
        assert result["missing_remote"] == 1

    def test_check_consistency(self) -> None:
        replicas = {"n1": {"a": 1}, "n2": {"a": 1}}
        result = self.checker.check_consistency(replicas)
        assert result["consistent"] is True

    def test_check_consistency_insufficient(self) -> None:
        result = self.checker.check_consistency({"n1": {"a": 1}})
        assert result["consistent"] is True

    def test_check_count(self) -> None:
        self.checker.check({})
        self.checker.check({})
        assert self.checker.check_count == 2

    def test_reset(self) -> None:
        self.checker.check({})
        self.checker.reset()
        assert self.checker.check_count == 0
