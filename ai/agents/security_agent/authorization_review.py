from __future__ import annotations

from typing import Any


class AuthorizationReview:
    """Reviews and evaluates authorization policies."""

    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}

    def add_policy(
        self,
        name: str,
        effect: str,
        action: str,
        resource: str,
    ) -> str:
        effect = effect.lower()
        if effect not in ("allow", "deny"):
            effect = "deny"
        self._policies[name] = {
            "name": name,
            "effect": effect,
            "action": action,
            "resource": resource,
        }
        return name

    def get_policy(self, name: str) -> dict[str, Any] | None:
        return self._policies.get(name)

    def list_policies(self) -> list[dict[str, Any]]:
        return list(self._policies.values())

    @property
    def policy_count(self) -> int:
        return len(self._policies)

    def review_policy(self, policy: dict[str, Any]) -> list[dict[str, Any]]:
        findings = []
        if policy.get("effect", "").lower() == "allow" and policy.get("resource", "") == "*":
            findings.append({
                "severity": "high",
                "message": "Wildcard resource in allow policy is dangerous",
            })
        if policy.get("action", "") == "*":
            findings.append({
                "severity": "medium",
                "message": "Wildcard action grants excessive permissions",
            })
        return findings

    def evaluate_access(
        self,
        subject: str,
        action: str,
        resource: str,
    ) -> dict[str, Any]:
        for policy in self._policies.values():
            if policy["action"] in (action, "*") and policy["resource"] in (resource, "*"):
                return {
                    "allowed": policy["effect"] == "allow",
                    "matched_policy": policy["name"],
                    "effect": policy["effect"],
                }
        return {"allowed": False, "matched_policy": None, "effect": "deny"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "policies": list(self._policies.values()),
            "policy_count": self.policy_count,
        }
