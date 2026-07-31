"""ABAC (Attribute-Based Access Control)."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from enum import Enum
from typing import Any


class ABACEffect(Enum):
    PERMIT = "permit"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"
    INDETERMINATE = "indeterminate"


class ABACPolicy:
    def __init__(self, name: str, target: dict[str, Any], effect: ABACEffect) -> None:
        self.policy_id = str(uuid.uuid4())[:8]
        self.name = name
        self.target = target
        self.effect = effect
        self.obligations: list[str] = []
        self.enabled = True


class ABACEngine:
    def __init__(self) -> None:
        self._policies: dict[str, ABACPolicy] = {}
        self._decisions: list[dict[str, Any]] = []
        self._attribute_providers: dict[str, Callable[..., Any]] = {}

    def add_policy(self, name: str, target: dict[str, Any], effect: ABACEffect) -> ABACPolicy:
        policy = ABACPolicy(name, target, effect)
        self._policies[policy.policy_id] = policy
        return policy

    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False

    def register_attribute_provider(self, name: str, provider: Callable[..., Any]) -> None:
        self._attribute_providers[name] = provider

    def evaluate(
        self, subject: dict[str, Any], resource: dict[str, Any], action: str, environment: dict[str, Any] | None = None
    ) -> ABACEffect:
        context = {"subject": subject, "resource": resource, "action": action, "environment": environment or {}}
        for policy in sorted(self._policies.values(), key=lambda p: p.policy_id):
            if not policy.enabled:
                continue
            if self._match_target(policy.target, context):
                decision = policy.effect
                self._decisions.append(
                    {
                        "policy_id": policy.policy_id,
                        "name": policy.name,
                        "effect": decision.value,
                        "context": context,
                        "timestamp": time.time(),
                    }
                )
                return decision
        self._decisions.append(
            {
                "policy_id": None,
                "name": "default",
                "effect": ABACEffect.DENY.value,
                "context": context,
                "timestamp": time.time(),
            }
        )
        return ABACEffect.DENY

    def _match_target(self, target: dict[str, Any], context: dict[str, Any]) -> bool:
        for key, value in target.items():
            parts = key.split(".")
            current = context
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return False
            if current != value:
                return False
        return True

    def get_decisions(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._decisions[-limit:]

    def list_policies(self) -> list[dict[str, Any]]:
        return [
            {"id": p.policy_id, "name": p.name, "effect": p.effect.value, "target": p.target, "enabled": p.enabled}
            for p in self._policies.values()
        ]
