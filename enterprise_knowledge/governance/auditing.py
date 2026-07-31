"""Audit logging for governance actions."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import (AccessLevel, AuditRecord)
from enterprise_knowledge.knowledge_protocols import new_id
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry


class AuditLogger:
    """Records governance/access events into the registry audit trail."""

    def __init__(self, registry: EnterpriseKnowledgeRegistry | None = None) -> None:
        self.registry = registry

    def log(self, actor: str, action: str, target: str = "",
            access_level: AccessLevel = AccessLevel.INTERNAL,
            outcome: str = "allowed") -> AuditRecord | None:
        if self.registry is None:
            return None
        entry = AuditRecord(audit_id=new_id("audit"), actor=actor,
                            action=action, target=target,
                            access_level=access_level,
                            outcome=outcome, created_at=time.time())
        self.registry.record_audit(entry)
        return entry

    def recent(self, limit: int = 10) -> list[AuditRecord]:
        if self.registry is None:
            return []
        audit = self.registry.list_audit()
        return audit[-max(0, limit):]

    def count(self) -> int:
        if self.registry is None:
            return 0
        return len(self.registry.list_audit())
