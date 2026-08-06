"""Audit manager: append-only in-memory audit trail."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.governance_config import GovernanceConfig


@dataclass(slots=True)
class AuditEntry:
    """One audit record."""

    action: str
    subject: str
    detail: str = ""
    sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "subject": self.subject,
            "detail": self.detail,
            "sequence": self.sequence,
        }


class AuditManager:
    """Append-only audit log with bounded retention."""

    def __init__(self, config: GovernanceConfig | None = None) -> None:
        self._config = config or GovernanceConfig()
        self._entries: list[AuditEntry] = []
        self._sequence = 0

    def record(self, action: str, subject: object, detail: str = "") -> None:
        if not self._config.audit_enabled:
            return
        self._sequence += 1
        name = getattr(subject, "title", None) or str(subject)
        self._entries.append(
            AuditEntry(action=action, subject=name, detail=detail, sequence=self._sequence)
        )
        while len(self._entries) > self._config.audit_keep_entries:
            self._entries.pop(0)

    def entries(self) -> list[AuditEntry]:
        return list(self._entries)
