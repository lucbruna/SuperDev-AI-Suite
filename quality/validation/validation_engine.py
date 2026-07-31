from __future__ import annotations

from typing import Any

from ..quality_models import GateDecision, ProductionGate


class ValidationEngine:
    """Pre-deploy validation — rules, policies, approval, production gate, compliance."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.validation
        self._rules: dict[str, Any] = {}
        self._policies: dict[str, Any] = {}
        self._approvals: dict[str, dict[str, Any]] = {}
        self._gates: dict[str, ProductionGate] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- rules ---------------------------------------------------------------

    def register_rule(self, name: str, rule: Any) -> None:
        self._rules[name] = rule
        self.engine.registry.register_rule(name, rule)

    def check_rule(self, name: str, context: dict[str, Any]) -> bool:
        rule = self._rules.get(name)
        if rule is None:
            return True
        if callable(rule):
            return bool(rule(context))
        if isinstance(rule, dict):
            field = rule.get("field")
            op = rule.get("op")
            expected = rule.get("value")
            actual = context.get(field)
            if op == "gte":
                return actual >= expected
            if op == "lte":
                return actual <= expected
            if op == "eq":
                return actual == expected
            if op == "min_pct":
                return (actual or 0) >= expected
        return False

    # -- policies ------------------------------------------------------------

    def set_policy(self, name: str, rules: list[str]) -> None:
        self._policies[name] = {"rules": list(rules)}

    def evaluate_policy(self, name: str, context: dict[str, Any]) -> dict[str, Any]:
        policy = self._policies.get(name)
        if policy is None:
            return {"policy": name, "passed": True, "failed_rules": []}
        failed = [
            rule for rule in policy["rules"]
            if not self.check_rule(rule, context)
        ]
        return {"policy": name, "passed": not failed, "failed_rules": failed}

    # -- approval ------------------------------------------------------------

    def require_approval(self, target: str, approver: str) -> dict[str, Any]:
        approval = {"target": target, "approver": approver, "approved": False}
        self._approvals[target] = approval
        return approval

    def approve(self, target: str, approver: str) -> bool:
        approval = self._approvals.get(target)
        if approval is None:
            return False
        if approval["approver"] != approver:
            return False
        approval["approved"] = True
        return True

    def is_approved(self, target: str) -> bool:
        approval = self._approvals.get(target)
        return bool(approval and approval["approved"])

    # -- production gate -----------------------------------------------------

    async def evaluate_gate(
        self,
        target: str,
        signals: dict[str, Any],
    ) -> ProductionGate:
        """Evaluate the production gate and decide APPROVED / BLOCKED."""
        score = signals.get("quality_score", 0.0)
        coverage = signals.get("coverage", 0.0)
        tests_passed = signals.get("tests_passed", True)
        blocked = signals.get("blocked", False)
        findings = signals.get("critical_findings", 0)

        checks = [
            {
                "name": "quality_score",
                "passed": score >= self.config.min_quality_score,
                "value": score,
            },
            {
                "name": "coverage",
                "passed": coverage >= self.config.min_coverage,
                "value": coverage,
            },
            {"name": "tests", "passed": tests_passed, "value": tests_passed},
            {"name": "security", "passed": not blocked, "value": blocked},
        ]
        blocked_reasons: list[str] = []
        for check in checks:
            if not check["passed"]:
                blocked_reasons.append(
                    f"{check['name']} failed (value={check.get('value')})"
                )
        if findings:
            blocked_reasons.append(f"{findings} critical finding(s)")

        gate = ProductionGate(
            target=target,
            checks=checks,
            quality_score=round(score, 4),
            decision=GateDecision.APPROVED if not blocked_reasons else GateDecision.BLOCKED,
            blocked_reasons=blocked_reasons,
        )
        self._gates[gate.gate_id] = gate
        self.engine.registry.register_gate(gate)
        self.engine.runtime.begin_gate()
        return gate

    # -- compliance ----------------------------------------------------------

    def compliance_report(self, target: str) -> dict[str, Any]:
        policies = {
            name: self.evaluate_policy(name, {"target": target})
            for name in self._policies
        }
        return {
            "target": target,
            "policies": policies,
            "compliant": all(p["passed"] for p in policies.values()),
        }

    def list_gates(self) -> list[ProductionGate]:
        return list(self._gates.values())

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "rules": len(self._rules),
            "policies": len(self._policies),
            "gates": len(self._gates),
            "approvals": len(self._approvals),
        }


__all__ = ["ValidationEngine"]
