"""Conflict Resolution - Data conflict detection and resolution."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConflictStrategy(Enum):
    CLIENT_WINS = "client_wins"
    SERVER_WINS = "server_wins"
    MERGE = "merge"
    MANUAL = "manual"
    TIMESTAMP = "timestamp"


@dataclass
class Conflict:
    conflict_id: str
    table: str
    record_id: str
    client_data: dict[str, Any] = field(default_factory=dict)
    server_data: dict[str, Any] = field(default_factory=dict)
    strategy: ConflictStrategy = ConflictStrategy.TIMESTAMP
    resolved: bool = False
    resolved_data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None


class ConflictResolver:
    def __init__(self, default_strategy: ConflictStrategy = ConflictStrategy.TIMESTAMP):
        self.conflicts: list[Conflict] = []
        self.default_strategy = default_strategy

    def detect(self, table: str, record_id: str, client_data: dict[str, Any], server_data: dict[str, Any]) -> Conflict:
        conflict_id = hashlib.sha256(f"{table}{record_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        conflict = Conflict(conflict_id=conflict_id, table=table, record_id=record_id, client_data=client_data, server_data=server_data, strategy=self.default_strategy)
        self.conflicts.append(conflict)
        return conflict

    def resolve(self, conflict_id: str, strategy: ConflictStrategy = None) -> dict[str, Any] | None:
        for conflict in self.conflicts:
            if conflict.conflict_id == conflict_id and not conflict.resolved:
                strat = strategy or conflict.strategy
                if strat == ConflictStrategy.CLIENT_WINS:
                    conflict.resolved_data = conflict.client_data
                elif strat == ConflictStrategy.SERVER_WINS:
                    conflict.resolved_data = conflict.server_data
                elif strat == ConflictStrategy.MERGE:
                    conflict.resolved_data = {**conflict.server_data, **conflict.client_data}
                elif strat == ConflictStrategy.TIMESTAMP:
                    conflict.resolved_data = conflict.client_data
                conflict.resolved = True
                conflict.resolved_at = datetime.now()
                return conflict.resolved_data
        return None

    def get_unresolved(self) -> list[Conflict]:
        return [c for c in self.conflicts if not c.resolved]

    def count(self) -> int:
        return len(self.conflicts)

    def count_unresolved(self) -> int:
        return len(self.get_unresolved())
