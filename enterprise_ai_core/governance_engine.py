"""
Governance Engine - Enforces enterprise governance rules and compliance
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import (
    Policy,
    PolicyAction,
    PolicyScope,
    PolicyEvaluation,
    Event,
    EventType,
    Severity,
)
from enterprise_ai_core.policy_engine import PolicyEngine
from enterprise_ai_core.audit_manager import AuditManager


class GovernanceEngine:
    """Central governance enforcement for all AI activities"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.policy_engine = orchestrator.policy_engine
        self.audit_manager = orchestrator.audit_manager
        self._governance_rules: Dict[str, Dict] = {}
        self._critical_operations: Dict[str, Dict] = {}

    async def initialize(self) -> None:
        await self._load_governance_rules()
        await self._register_critical_operations()

    async def shutdown(self) -> None:
        pass

    async def _load_governance_rules(self) -> None:
        self._governance_rules = {
            "require_approval": {
                "thresholds": {
                    "financial": 100000,
                    "contract": 50000,
                    "data_access": 1000,
                    "user_impact": 100,
                },
                "actions": ["financial_transaction", "contract_signing", "data_export", "user_data_access"],
            },
            "data_protection": {
                "pii_fields": ["ssn", "credit_card", "medical_record", "personal_email", "phone"],
                "encryption_required": True,
                "access_logging": True,
            },
            "agent_behavior": {
                "max_consecutive_errors": 5,
                "max_execution_time": 3600,
                "require_human_review": ["delete_data", "modify_production", "send_external"],
            },
            "compliance": {
                "standards": ["SOC2", "GDPR", "HIPAA", "PCI-DSS"],
                "audit_all_decisions": True,
                "retention_days": 2555,
            },
        }

    async def _register_critical_operations(self) -> None:
        self._critical_operations = {
            "delete_user_data": {
                "requires_approval": True,
                "approvers": ["data_protection_officer", "security_lead"],
                "audit_level": "full",
            },
            "modify_production_config": {
                "requires_approval": True,
                "approvers": ["platform_lead", "security_lead"],
                "audit_level": "full",
            },
            "financial_transaction": {
                "requires_approval": True,
                "threshold": 100000,
                "approvers": ["finance_director", "ceo"],
                "audit_level": "full",
            },
            "external_api_call": {
                "requires_approval": False,
                "allowed_domains": [],
                "audit_level": "standard",
            },
            "model_deployment": {
                "requires_approval": True,
                "approvers": ["ml_lead", "security_lead"],
                "audit_level": "full",
            },
        }

    async def evaluate_action(
        self,
        action: str,
        context: Dict[str, Any],
        actor_id: Optional[UUID] = None,
    ) -> PolicyEvaluation:
        """Evaluate if an action is allowed under governance rules"""

        policy = await self.policy_engine.evaluate(action, context)

        is_critical = action in self._critical_operations
        critical_config = self._critical_operations.get(action, {})

        if is_critical and critical_config.get("requires_approval"):
            threshold = critical_config.get("threshold", 0)
            value = context.get("value", 0) or context.get("amount", 0)

            if value >= threshold:
                policy.action = PolicyAction.REQUIRE_APPROVAL
                policy.reason = f"Critical operation {action} requires approval (value: {value})"

        await self.audit_manager.log(
            event_type="governance.evaluation",
            action="evaluate_action",
            details={
                "action": action,
                "result": policy.action.value,
                "reason": policy.reason,
                "actor_id": str(actor_id) if actor_id else None,
            },
        )

        return policy

    async def enforce_policy(self, evaluation: PolicyEvaluation) -> bool:
        """Enforce policy decision"""
        if evaluation.action == PolicyAction.DENY:
            await self.orchestrator.publish_event(
                Event(
                    type=EventType.POLICY_VIOLATION,
                    severity=Severity.ERROR,
                    payload={
                        "policy": evaluation.policy_name,
                        "action": evaluation.action.value,
                        "reason": evaluation.reason,
                    },
                )
            )
            return False

        if evaluation.action == PolicyAction.REQUIRE_APPROVAL:
            return await self._request_approval(evaluation)

        return True

    async def _request_approval(self, evaluation: PolicyEvaluation) -> bool:
        """Request human approval for critical actions"""
        return False

    async def check_compliance(self, operation: str, data: Dict) -> Dict[str, Any]:
        """Check compliance for an operation"""
        results = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "standards": self._governance_rules["compliance"]["standards"],
        }

        if "pii" in data:
            for field in self._governance_rules["data_protection"]["pii_fields"]:
                if field in str(data).lower():
                    results["warnings"].append(f"PII field detected: {field}")
                    if not self._governance_rules["data_protection"]["encryption_required"]:
                        results["violations"].append(f"Unencrypted PII: {field}")
                        results["compliant"] = False

        return results

    def get_governance_status(self) -> Dict[str, Any]:
        return {
            "rules_loaded": len(self._governance_rules),
            "critical_operations": len(self._critical_operations),
            "compliance_standards": self._governance_rules["compliance"]["standards"],
            "audit_enabled": self._governance_rules["compliance"]["audit_all_decisions"],
        }