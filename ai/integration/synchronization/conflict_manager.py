"""
Conflict Manager - Sync conflict resolution
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class ResolutionStrategy(Enum):
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    NEWEST_WINS = "newest_wins"
    MANUAL = "manual"
    MERGE = "merge"


@dataclass
class Conflict:
    conflict_id: str
    record_id: str
    source_data: Dict[str, Any] = field(default_factory=dict)
    target_data: Dict[str, Any] = field(default_factory=dict)
    strategy: ResolutionStrategy = ResolutionStrategy.MANUAL
    resolved: bool = False
    resolution: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class ConflictManager:
    def __init__(self):
        self.conflicts: Dict[str, Conflict] = {}
        self.default_strategy: ResolutionStrategy = ResolutionStrategy.NEWEST_WINS

    def detect_conflict(self, record_id: str, source_data: Dict[str, Any], target_data: Dict[str, Any]) -> Conflict:
        conflict_id = hashlib.sha256(f"{record_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        conflict = Conflict(conflict_id=conflict_id, record_id=record_id, source_data=source_data, target_data=target_data, strategy=self.default_strategy)
        self.conflicts[conflict_id] = conflict
        return conflict

    def resolve(self, conflict_id: str, resolution: Dict[str, Any]) -> bool:
        conflict = self.conflicts.get(conflict_id)
        if conflict:
            conflict.resolved = True
            conflict.resolution = resolution
            conflict.resolved_at = datetime.now()
            return True
        return False

    def auto_resolve(self, conflict_id: str) -> bool:
        conflict = self.conflicts.get(conflict_id)
        if not conflict:
            return False
        if conflict.strategy == ResolutionStrategy.SOURCE_WINS:
            conflict.resolution = conflict.source_data
        elif conflict.strategy == ResolutionStrategy.TARGET_WINS:
            conflict.resolution = conflict.target_data
        else:
            conflict.resolution = conflict.source_data
        conflict.resolved = True
        conflict.resolved_at = datetime.now()
        return True

    def set_strategy(self, strategy: ResolutionStrategy) -> None:
        self.default_strategy = strategy

    def get_unresolved(self) -> List[Conflict]:
        return [c for c in self.conflicts.values() if not c.resolved]

    def get_conflict(self, conflict_id: str) -> Optional[Conflict]:
        return self.conflicts.get(conflict_id)

    def count(self) -> int:
        return len(self.conflicts)
