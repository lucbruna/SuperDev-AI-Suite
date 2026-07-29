from __future__ import annotations

import logging
import uuid
from threading import Lock
from datetime import datetime
from typing import Any, Dict, List, Optional

from .knowledge_models import KnowledgeEntry

logger = logging.getLogger(__name__)


class KnowledgeContext:
    def __init__(self):
        self._lock = Lock()
        self._contexts: Dict[str, Dict[str, Any]] = {}
        self._links: Dict[str, List[str]] = {}

    def create_context(self, name: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
        ctx_id = str(uuid.uuid4())
        with self._lock:
            self._contexts[ctx_id] = {
                "id": ctx_id,
                "name": name or f"context-{ctx_id[:8]}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": metadata or {},
                "entries": [],
                "active": True,
            }
            self._links[ctx_id] = []
        return ctx_id

    def get_context(self, ctx_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            ctx = self._contexts.get(ctx_id)
            return dict(ctx) if ctx else None

    def update_context(self, ctx_id: str, metadata: Dict[str, Any]) -> bool:
        with self._lock:
            ctx = self._contexts.get(ctx_id)
            if not ctx:
                return False
            ctx["metadata"].update(metadata)
            ctx["updated_at"] = datetime.utcnow()
            return True

    def close_context(self, ctx_id: str) -> bool:
        with self._lock:
            ctx = self._contexts.get(ctx_id)
            if not ctx:
                return False
            ctx["active"] = False
            ctx["updated_at"] = datetime.utcnow()
            return True

    def link_related(self, ctx_id: str, related_id: str) -> bool:
        with self._lock:
            if ctx_id not in self._links:
                return False
            if related_id not in self._links[ctx_id]:
                self._links[ctx_id].append(related_id)
            return True

    def get_active_contexts(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(ctx) for ctx in self._contexts.values() if ctx.get("active")]

    def add_entry_to_context(self, ctx_id: str, entry: KnowledgeEntry) -> bool:
        with self._lock:
            ctx = self._contexts.get(ctx_id)
            if not ctx:
                return False
            ctx["entries"].append(entry.id)
            ctx["updated_at"] = datetime.utcnow()
            return True

    def get_context_entries(self, ctx_id: str) -> List[str]:
        with self._lock:
            ctx = self._contexts.get(ctx_id)
            return list(ctx["entries"]) if ctx else []

    def get_related_contexts(self, ctx_id: str) -> List[str]:
        with self._lock:
            return list(self._links.get(ctx_id, []))

    def cleanup_expired(self, max_age_minutes: int = 1440) -> int:
        now = datetime.utcnow()
        expired = []
        with self._lock:
            for ctx_id, ctx in self._contexts.items():
                age = (now - ctx["updated_at"]).total_seconds() / 60
                if age > max_age_minutes and not ctx.get("active", True):
                    expired.append(ctx_id)
            for ctx_id in expired:
                del self._contexts[ctx_id]
                self._links.pop(ctx_id, None)
        return len(expired)

    def clear(self) -> None:
        with self._lock:
            self._contexts.clear()
            self._links.clear()