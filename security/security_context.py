"""Request-scoped context for the Security Engine (Volume 16)."""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any

_current_scan_id: ContextVar[str] = ContextVar("_security_scan_id", default="")
_current_actor: ContextVar[str] = ContextVar("_security_actor", default="system")


class SecurityContext:
    """Per-operation context: scan id, actor, and extra metadata."""

    def __init__(self) -> None:
        self._scan_id = _current_scan_id
        self._actor = _current_actor

    def begin_scan(self, actor: str = "system") -> str:
        scan_id = uuid.uuid4().hex[:16]
        self._scan_id.set(scan_id)
        self._actor.set(actor)
        return scan_id

    def end_scan(self) -> None:
        self._scan_id.set("")
        self._actor.set("system")

    @property
    def scan_id(self) -> str:
        return self._scan_id.get()

    @property
    def actor(self) -> str:
        return self._actor.get()

    def snapshot(self) -> dict[str, Any]:
        return {"scan_id": self.scan_id, "actor": self.actor}
