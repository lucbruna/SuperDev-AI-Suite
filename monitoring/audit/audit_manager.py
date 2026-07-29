import uuid
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from .audit_repository import AuditRepository
from .audit_export import AuditExport


@dataclass
class AuditEntry:
    id: str
    action: str
    actor_id: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    timestamp: float


class AuditManager:
    def __init__(self) -> None:
        self._repository = AuditRepository()
        self._export = AuditExport()

    def log(self, action: str, actor_id: str, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            action=action,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            timestamp=time.time(),
        )
        self._repository.save(entry)
        return entry

    def query(self, filters: Optional[Dict[str, Any]] = None) -> List[AuditEntry]:
        results = self._repository.list()
        if filters:
            for key, value in filters.items():
                results = [e for e in results if getattr(e, key, None) == value]
        return results

    def export(self, filters: Optional[Dict[str, Any]] = None, format: str = "json") -> str:
        entries = self.query(filters)
        if format == "json":
            return self._export.to_json(entries)
        elif format == "csv":
            return self._export.to_csv(entries)
        elif format == "markdown":
            return self._export.to_markdown(entries)
        raise ValueError(f"Unsupported format: {format}")
