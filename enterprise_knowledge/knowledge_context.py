"""Context for the Knowledge Graph & Enterprise Memory Engine.

Carries attributes per query/session (actor, workspace, access level...)
so subsystems can make governance-aware decisions.
"""

from __future__ import annotations

import threading
from typing import Any

from enterprise_knowledge.knowledge_models import AccessLevel


class EnterpriseKnowledgeContext:
    """Thread-local context attributes."""

    def __init__(self) -> None:
        self._local = threading.local()

    def _defaults(self) -> dict[str, Any]:
        return {
            "actor": "anonymous",
            "role": "guest",
            "workspace": "default",
            "access_level": AccessLevel.PUBLIC,
        }

    def get(self, key: str, default: Any = None) -> Any:
        data = getattr(self._local, "data", None)
        if data is None:
            return default
        return data.get(key, default)

    def set(self, **fields: Any) -> None:
        data = getattr(self._local, "data", None)
        if data is None:
            data = self._defaults()
            self._local.data = data
        data.update(fields)

    def snapshot(self) -> dict[str, Any]:
        return dict(getattr(self._local, "data", self._defaults()))

    def clear(self) -> None:
        self._local.data = self._defaults()
