"""Transfer learning between domains."""

from __future__ import annotations

from typing import Any


class TransferLearning:
    """Facilitates knowledge transfer between different agent domains."""

    def __init__(self) -> None:
        self._domain_knowledge: dict[str, dict[str, Any]] = {}
        self._transfer_count: int = 0

    def register_domain(self, domain: str, knowledge: dict[str, Any]) -> None:
        self._domain_knowledge[domain] = knowledge

    def transfer(self, source_domain: str, target_domain: str) -> dict[str, Any]:
        self._transfer_count += 1
        source = self._domain_knowledge.get(source_domain, {})
        if not source:
            return {"status": "no_source", "transferred_items": 0}
        target = self._domain_knowledge.get(target_domain, {})
        shared_keys = set(source.keys()) - set(target.keys())
        transferred: list[str] = []
        for key in shared_keys:
            target[key] = source[key]
            transferred.append(key)
        self._domain_knowledge[target_domain] = target
        return {
            "status": "transferred",
            "source": source_domain,
            "target": target_domain,
            "transferred_items": len(transferred),
            "items": transferred,
        }

    def get_domain_knowledge(self, domain: str) -> dict[str, Any]:
        return dict(self._domain_knowledge.get(domain, {}))

    def snapshot(self) -> dict[str, Any]:
        return {
            "domains": list(self._domain_knowledge.keys()),
            "total_transfers": self._transfer_count,
        }
