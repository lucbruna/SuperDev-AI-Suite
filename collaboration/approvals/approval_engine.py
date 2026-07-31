"""Approval engine: aprovações em cadeia.

Fluxo do exemplo: Developer -> Tech Lead -> Security -> Diretor.
Humanos aprovam; agentes de IA podem apenas solicitar/recomendar.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (ApprovalRecord, EntityKind)
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.approvals.approval_manager import ApprovalManager
from collaboration.approvals.approval_policy import ApprovalPolicy


class ApprovalEngine:
    """Orquestrador de aprovações (Fase 6 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: ApprovalManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.manager = manager or ApprovalManager(registry=registry)
        self.policy = ApprovalPolicy()

    def start(self, target_kind: EntityKind, target_id: str,
              requested_by: str, flow: str = "manager") -> ApprovalRecord:
        approval = self.manager.start(target_kind, target_id,
                                      requested_by, flow)
        self.metrics.increment("collab.approvals")
        self.events.publish(CollaborationEventType.APPROVAL_STARTED,
                            {"approval_id": approval.approval_id,
                             "target_kind": target_kind.value,
                             "target_id": target_id, "flow": flow})
        return approval

    def get(self, approval_id: str) -> ApprovalRecord | None:
        return self.manager.get(approval_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, approval_id: str) -> bool:
        return self.manager.remove(approval_id)

    def decide(self, approval_id: str, approved: bool, decider: str,
               reason: str = "") -> ApprovalRecord | None:
        approval = self.manager.decide(approval_id, approved, decider,
                                       reason)
        if approval is not None:
            self.events.publish(CollaborationEventType.APPROVAL_DECIDED,
                                {"approval_id": approval_id,
                                 "status": approval.status.value,
                                 "decided_by": decider})
        return approval

    def cancel(self, approval_id: str, decider: str) -> ApprovalRecord | None:
        return self.manager.cancel(approval_id, decider)

    def history(self, approval_id: str) -> Any:
        return self.manager.history(approval_id)

    def steps(self, flow: str) -> list[dict[str, Any]]:
        return self.manager.flow.steps_for(flow)

    def roles(self, flow: str) -> list[Any]:
        return self.manager.flow.roles(flow)

    def by_target(self, target_id: str) -> list[ApprovalRecord]:
        return self.manager.by_target(target_id)

    def can_approve(self, member: Any, target_kind: EntityKind) -> bool:
        return self.policy.can_approve(member, target_kind)

    def stats(self) -> dict[str, Any]:
        return {"approvals": self.manager.count()}
