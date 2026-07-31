"""Search filters over metadata, types and access levels."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_models import AccessLevel


class SearchFilters:
    """Post-filters result lists by metadata keys and access level."""

    def apply(self, results: list[dict[str, Any]],
              filters: dict[str, Any] | None = None,
              min_access: AccessLevel = AccessLevel.PUBLIC) -> list[dict[str, Any]]:
        filtered = []
        for item in results:
            metadata = item.get("metadata", {}) or {}
            if filters:
                matched = True
                for key, value in filters.items():
                    if metadata.get(key) != value:
                        matched = False
                        break
                if not matched:
                    continue
            access = metadata.get("access_level",
                                  AccessLevel.PUBLIC.value)
            if self._access_rank(access) < self._access_rank(min_access.value):
                continue
            filtered.append(item)
        return filtered

    @staticmethod
    def _access_rank(value: str) -> int:
        order = {"public": 0, "internal": 1, "confidential": 2,
                 "restricted": 3}
        return order.get(str(value).lower(), 0)
