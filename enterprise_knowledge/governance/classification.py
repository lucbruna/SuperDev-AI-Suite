"""Classification rules that map content to access levels."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_models import AccessLevel


class GovernanceClassification:
    """Keyword-based classification into access levels."""

    def __init__(self) -> None:
        self._rules: dict[AccessLevel, list[str]] = {
            AccessLevel.CONFIDENTIAL: ["salário", "folha", "sigiloso",
                                       "confidencial"],
            AccessLevel.RESTRICTED: ["estratégia", "board", "diretores",
                                     "restrito"],
            AccessLevel.INTERNAL: ["projeto", "módulo", "contrato",
                                   "interno"],
        }

    def add_rule(self, level: AccessLevel, keywords: list[str]) -> None:
        self._rules.setdefault(level, []).extend(keywords)

    def classify(self, text: str) -> AccessLevel:
        text_lower = (text or "").lower()
        for level in (AccessLevel.RESTRICTED, AccessLevel.CONFIDENTIAL,
                      AccessLevel.INTERNAL):
            if any(keyword in text_lower for keyword in self._rules.get(level, [])):
                return level
        return AccessLevel.PUBLIC

    def rules(self) -> dict[str, list[str]]:
        return {level.value: list(keywords)
                for level, keywords in self._rules.items()}
