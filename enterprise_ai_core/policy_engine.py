"""
Policy Engine - Evaluates and enforces business policies and rules
"""

import re
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
)
from enterprise_ai_core.policies.rule_manager import RuleManager
from enterprise_ai_core.policies.compliance_checker import ComplianceChecker


class PolicyEngine:
    """Evaluates policies against actions and context"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.rule_manager = RuleManager()
        self.compliance_checker = ComplianceChecker()
        self._policies: Dict[UUID, Policy] = {}
        self._policy_cache: Dict[str, List[Policy]] = {}

    async def initialize(self) -> None:
        await self.rule_manager.initialize()
        await self.compliance_checker.initialize()
        await self._load_default_policies()

    async def shutdown(self) -> None:
        pass

    async def _load_default_policies(self) -> None:
        default_policies = [
            Policy(
                name="financial_threshold",
                description="Require approval for financial transactions over threshold",
                scope=PolicyScope.GLOBAL,
                action=PolicyAction.REQUIRE_APPROVAL,
                conditions={"action": "financial_transaction", "amount": {">": 100000}},
                priority=10,
            ),
            Policy(
                name="data_access_pii",
                description="Restrict access to PII data",
                scope=PolicyScope.GLOBAL,
                action=PolicyAction.DENY,
                conditions={"resource_type": "pii", "role": {"!in": ["admin", "data_officer"]}},
                priority=20,
            ),
            Policy(
                name="production_modification",
                description="Require approval for production changes",
                scope=PolicyScope.GLOBAL,
                action=PolicyAction.REQUIRE_APPROVAL,
                conditions={"environment": "production", "action": {"in": ["deploy", "config_change", "database_migration"]}},
                priority=15,
            ),
            Policy(
                name="external_communication",
                description="Log all external API calls",
                scope=PolicyScope.GLOBAL,
                action=PolicyAction.LOG_ONLY,
                conditions={"action": "external_api_call"},
                priority=100,
            ),
            Policy(
                name="agent_error_threshold",
                description="Alert on consecutive agent errors",
                scope=PolicyScope.AGENT,
                action=PolicyAction.LOG_ONLY,
                conditions={"consecutive_errors": {">=": 5}},
                priority=50,
            ),
        ]

        for policy in default_policies:
            await self.register_policy(policy)

    async def register_policy(self, policy: Policy) -> None:
        self._policies[policy.id] = policy
        self._invalidate_cache(policy.scope)

    async def unregister_policy(self, policy_id: UUID) -> bool:
        policy = self._policies.pop(policy_id, None)
        if policy:
            self._invalidate_cache(policy.scope)
            return True
        return False

    def get_policy(self, policy_id: UUID) -> Optional[Policy]:
        return self._policies.get(policy_id)

    def list_policies(self, scope: Optional[PolicyScope] = None, enabled_only: bool = True) -> List[Policy]:
        policies = list(self._policies.values())
        if enabled_only:
            policies = [p for p in policies if p.enabled]
        if scope:
            policies = [p for p in policies if p.scope == scope]
        return sorted(policies, key=lambda p: p.priority)

    async def evaluate(
        self,
        action: str,
        context: Dict[str, Any],
        scope: Optional[PolicyScope] = None,
    ) -> PolicyEvaluation:
        """Evaluate all applicable policies for an action"""
        applicable = self._get_applicable_policies(action, context, scope)

        for policy in applicable:
            if await self._matches_policy(policy, action, context):
                evaluation = PolicyEvaluation(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    action=policy.action,
                    matched=True,
                    reason=f"Policy {policy.name} matched",
                    context=context,
                )

                await self.orchestrator.publish_event(
                    Event(
                        type=EventType.POLICY_EVALUATED,
                        payload={
                            "policy_id": str(policy.id),
                            "policy_name": policy.name,
                            "action": policy.action.value,
                            "matched": True,
                        }
                    )
                )

                return evaluation

        return PolicyEvaluation(
            policy_id=UUID(int=0),
            policy_name="default_allow",
            action=PolicyAction.ALLOW,
            matched=False,
            reason="No matching policies, default allow",
            context=context,
        )

    def _get_applicable_policies(
        self,
        action: str,
        context: Dict[str, Any],
        scope: Optional[PolicyScope],
    ) -> List[Policy]:
        cache_key = f"{scope.value if scope else 'global'}:{action}"

        if cache_key in self._policy_cache:
            return self._policy_cache[cache_key]

        policies = self.list_policies(scope)
        applicable = [p for p in policies if self._policy_applies_to_action(p, action)]

        self._policy_cache[cache_key] = applicable
        return applicable

    def _policy_applies_to_action(self, policy: Policy, action: str) -> bool:
        if not policy.enabled:
            return False
        if "action" in policy.conditions:
            cond_action = policy.conditions["action"]
            if isinstance(cond_action, str):
                return cond_action == action or cond_action == "*"
            elif isinstance(cond_action, list):
                return action in cond_action
        return True

    async def _matches_policy(
        self,
        policy: Policy,
        action: str,
        context: Dict[str, Any],
    ) -> bool:
        for key, condition in policy.conditions.items():
            if key == "action":
                continue

            context_value = context.get(key)
            if context_value is None:
                return False

            if not self._evaluate_condition(context_value, condition):
                return False

        return True

    def _evaluate_condition(self, value: Any, condition: Any) -> bool:
        if isinstance(condition, dict):
            for op, expected in condition.items():
                if op in (">", ">=", "<", "<=", "==", "!="):
                    if not self._compare(value, expected, op):
                        return False
                elif op == "in":
                    if value not in expected:
                        return False
                elif op == "!in":
                    if value in expected:
                        return False
                elif op == "contains":
                    if expected not in str(value):
                        return False
                elif op == "regex":
                    if not re.search(expected, str(value)):
                        return False
            return True
        else:
            return value == condition

    def _compare(self, a: Any, b: Any, op: str) -> bool:
        try:
            if op == ">":
                return a > b
            elif op == ">=":
                return a >= b
            elif op == "<":
                return a < b
            elif op == "<=":
                return a <= b
            elif op == "==":
                return a == b
            elif op == "!=":
                return a != b
        except Exception:
            return False
        return False

    def _invalidate_cache(self, scope: PolicyScope) -> None:
        keys_to_remove = [k for k in self._policy_cache if k.startswith(scope.value)]
        for key in keys_to_remove:
            self._policy_cache.pop(key, None)

    async def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.compliance_checker.check(data)