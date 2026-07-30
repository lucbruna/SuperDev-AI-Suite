from __future__ import annotations

from typing import Any, Dict, List

from .cluster_sync import ClusterSync
from .conflict_resolution import ConflictResolution
from .consistency_checker import ConsistencyChecker
from .distributed_memory import DistributedMemory
from .node_sync import NodeSync
from .replication import Replication
from .transaction_manager import TransactionManager


class SynchronizationEngine:
    """Facade for memory synchronization across nodes and clusters."""

    def __init__(self):
        self._replication = Replication()
        self._distributed = DistributedMemory()
        self._node_sync = NodeSync()
        self._cluster_sync = ClusterSync()
        self._transactions = TransactionManager()
        self._conflicts = ConflictResolution()
        self._consistency = ConsistencyChecker()
        self._sync_count: int = 0

    @property
    def replication(self) -> Replication:
        return self._replication

    @property
    def distributed(self) -> DistributedMemory:
        return self._distributed

    @property
    def node_sync(self) -> NodeSync:
        return self._node_sync

    @property
    def cluster_sync(self) -> ClusterSync:
        return self._cluster_sync

    @property
    def transactions(self) -> TransactionManager:
        return self._transactions

    @property
    def conflicts(self) -> ConflictResolution:
        return self._conflicts

    @property
    def consistency(self) -> ConsistencyChecker:
        return self._consistency

    def synchronize(self, local: Dict[str, Any], remote: Dict[str, Any]) -> Dict[str, Any]:
        merged = self._replication.merge(local, remote)
        conflicts = self._conflicts.detect(local, remote)
        if conflicts:
            merged = self._conflicts.resolve(merged, conflicts)
        self._sync_count += 1
        return {
            "merged": merged,
            "conflicts_resolved": len(conflicts),
            "sync_id": self._sync_count,
            "consistent": self._consistency.check(merged),
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "sync_count": self._sync_count,
            "replication_count": self._replication.replication_count,
            "active_transactions": self._transactions.active_count,
            "nodes_known": self._node_sync.node_count,
            "clusters_known": self._cluster_sync.cluster_count,
        }
