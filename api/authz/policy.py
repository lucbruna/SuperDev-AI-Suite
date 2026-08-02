from __future__ import annotations

from typing import Any


class Policy:
    """A single authorization policy with effect, actions, and resources."""

    def __init__(
        self,
        id: str,
        effect: str = "Allow",
        actions: list[str] | None = None,
        resources: list[str] | None = None,
    ) -> None:
        self.id = id
        self.effect = effect
        self.actions = actions or []
        self.resources = resources or []

    def _match_pattern(self, value: str, pattern: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith(":*"):
            return value == pattern[:-2] or value.startswith(pattern[:-2] + ":")
        return value == pattern

    def matches(self, action: str, resource: str) -> bool:
        action_ok = any(self._match_pattern(action, p) for p in self.actions) if self.actions else False
        resource_ok = any(self._match_pattern(resource, p) for p in self.resources) if self.resources else False
        return action_ok and resource_ok

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "effect": self.effect,
            "actions": list(self.actions),
            "resources": list(self.resources),
        }


class PolicyBuilder:
    """Fluent builder for Policy objects."""

    def __init__(self) -> None:
        self._id = ""
        self._effect = "Allow"
        self._actions: list[str] = []
        self._resources: list[str] = []

    def id(self, value: str) -> PolicyBuilder:
        self._id = value
        return self

    def effect(self, value: str) -> PolicyBuilder:
        self._effect = value
        return self

    def actions(self, *actions: str) -> PolicyBuilder:
        self._actions.extend(actions)
        return self

    def resources(self, *resources: str) -> PolicyBuilder:
        self._resources.extend(resources)
        return self

    def build(self) -> Policy:
        return Policy(id=self._id, effect=self._effect, actions=self._actions, resources=self._resources)


class PolicyEngine:
    """Evaluates actions/resources against a set of policies.

    Deny always overrides Allow. No matching policy evaluates to False.
    """

    def __init__(self) -> None:
        self._policies: list[Policy] = []

    def add(self, policy: Policy) -> None:
        self._policies.append(policy)

    def evaluate(self, action: str, resource: str) -> bool:
        allowed = False
        for policy in self._policies:
            if not policy.matches(action, resource):
                continue
            if policy.effect == "Deny":
                return False
            allowed = True
        return allowed

    def list_policies(self) -> list[Policy]:
        return list(self._policies)

    def to_dict(self) -> dict[str, Any]:
        return {"policies": [p.to_dict() for p in self._policies], "count": len(self._policies)}
