"""
AI Decision Audit System
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import json


class AuditAction(Enum):
    PREDICTION = "prediction"
    TRAINING = "training"
    DEPLOYMENT = "deployment"
    RETRIEVAL = "retrieval"
    RETRAINING = "retraining"


@dataclass
class AuditEntry:
    entry_id: str
    model_id: str
    action: AuditAction
    input_hash: str = ""
    output_hash: str = ""
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    explainability: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    model_id: str
    total_entries: int
    actions: Dict[str, int] = field(default_factory=dict)
    time_range: str = ""
    entries: List[AuditEntry] = field(default_factory=list)


class AIAudit:
    def __init__(self):
        self.entries: List[AuditEntry] = []
        self.immutable_log: List[str] = []

    def log_decision(self, model_id: str, action: AuditAction, input_data: str = "", output: str = "", user_id: str = "", metadata: Dict[str, Any] = None, explainability: Dict[str, Any] = None) -> AuditEntry:
        entry_id = hashlib.sha256(f"{model_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        input_hash = hashlib.sha256(input_data.encode()).hexdigest() if input_data else ""
        output_hash = hashlib.sha256(output.encode()).hexdigest() if output else ""
        entry = AuditEntry(entry_id=entry_id, model_id=model_id, action=action, input_hash=input_hash, output_hash=output_hash, user_id=user_id, metadata=metadata or {}, explainability=explainability or {})
        self.entries.append(entry)
        self.immutable_log.append(json.dumps({"entry_id": entry_id, "model_id": model_id, "action": action.value, "timestamp": entry.timestamp.isoformat()}))
        return entry

    def get_entries(self, model_id: str = None, action: AuditAction = None) -> List[AuditEntry]:
        results = self.entries
        if model_id:
            results = [e for e in results if e.model_id == model_id]
        if action:
            results = [e for e in results if e.action == action]
        return results

    def generate_report(self, model_id: str) -> AuditReport:
        entries = [e for e in self.entries if e.model_id == model_id]
        actions = {}
        for e in entries:
            actions[e.action.value] = actions.get(e.action.value, 0) + 1
        return AuditReport(model_id=model_id, total_entries=len(entries), actions=actions, entries=entries)

    def verify_integrity(self) -> bool:
        return len(self.entries) == len(self.immutable_log)

    def get_explainability(self, entry_id: str) -> Dict[str, Any]:
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry.explainability
        return {}

    def search(self, query: str) -> List[AuditEntry]:
        return [e for e in self.entries if query in json.dumps(e.metadata)]

    def count(self) -> int:
        return len(self.entries)
