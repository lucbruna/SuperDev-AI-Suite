"""Decision engine."""

import time
from datetime import datetime

from .models import (
    DecisionPolicy,
    DecisionRequest,
    DecisionResult,
    DecisionStatus,
    RiskLevel,
    Rule,
)


class DecisionEngine:
    def __init__(self):
        self._policies: dict[str, DecisionPolicy] = {}
        self._rules: dict[str, Rule] = {}
        self._history: list[DecisionResult] = []

    def add_policy(self, policy: DecisionPolicy) -> DecisionPolicy:
        self._policies[policy.policy_id] = policy
        for rule in policy.rules:
            self._rules[rule.rule_id] = rule
        return policy

    def add_rule(self, rule: Rule) -> Rule:
        self._rules[rule.rule_id] = rule
        return rule

    def get_policy(self, policy_id: str) -> DecisionPolicy | None:
        return self._policies.get(policy_id)

    def get_rule(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def evaluate(self, request: DecisionRequest) -> DecisionResult:
        start = time.time()
        context = request.context
        applied_rules = []
        reasoning = []

        all_rules = list(self._rules.values()) + request.rules
        all_rules.sort(key=lambda r: r.priority, reverse=True)

        decision = "default_action"
        confidence = 0.5

        for rule in all_rules:
            if not rule.enabled:
                continue
            if rule.condition and self._check_condition(rule.condition, context):
                applied_rules.append(rule.rule_id)
                reasoning.append(f"Rule '{rule.name}' matched: {rule.condition}")
                decision = rule.action
                confidence = min(1.0, confidence + 0.2)
                break

        status = DecisionStatus.APPROVED if confidence > 0.6 else DecisionStatus.PENDING
        if request.risk_level == RiskLevel.CRITICAL:
            status = DecisionStatus.PENDING
            reasoning.append("Critical risk level - requires manual approval")

        elapsed = (time.time() - start) * 1000
        result = DecisionResult(
            request_id=request.request_id,
            status=status,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            applied_rules=applied_rules,
            execution_time_ms=elapsed,
        )
        self._history.append(result)
        return result

    def get_history(self, limit: int = 100) -> list[DecisionResult]:
        return self._history[-limit:]

    def get_history_by_status(self, status: DecisionStatus) -> list[DecisionResult]:
        return [r for r in self._history if r.status == status]

    def approve(self, request_id: str) -> DecisionResult | None:
        for r in self._history:
            if r.request_id == request_id and r.status == DecisionStatus.PENDING:
                r.status = DecisionStatus.APPROVED
                r.executed_at = datetime.now()
                return r
        return None

    def reject(self, request_id: str) -> DecisionResult | None:
        for r in self._history:
            if r.request_id == request_id and r.status == DecisionStatus.PENDING:
                r.status = DecisionStatus.REJECTED
                return r
        return None

    def _check_condition(self, condition: str, context: dict) -> bool:
        parts = condition.split()
        if len(parts) == 3:
            key, op, val = parts
            ctx_val = context.get(key)
            if ctx_val is None:
                return False
            try:
                if op == ">":
                    return float(ctx_val) > float(val)
                elif op == "<":
                    return float(ctx_val) < float(val)
                elif op == "==":
                    return str(ctx_val) == val.strip('"').strip("'")
                elif op == ">=":
                    return float(ctx_val) >= float(val)
                elif op == "<=":
                    return float(ctx_val) <= float(val)
            except (ValueError, TypeError):
                return False
        elif condition in context:
            return bool(context[condition])
        return False
