from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Literal


SharePermission = Literal["view", "edit", "admin"]


@dataclass
class ShareLink:
    token: str = ""
    dashboard_id: str = ""
    permission: SharePermission = "view"
    expires_at: float = 0.0
    created_at: float = field(default_factory=time.time)
    created_by: str = ""


class DashboardShare:
    """Manages dashboard sharing and access links."""

    def __init__(self) -> None:
        self._links: dict[str, ShareLink] = {}

    def create_link(
        self,
        dashboard_id: str,
        permission: SharePermission = "view",
        expires_in_seconds: float = 86400.0,
        created_by: str = "",
    ) -> ShareLink:
        import uuid
        link = ShareLink(
            token=uuid.uuid4().hex[:16],
            dashboard_id=dashboard_id,
            permission=permission,
            expires_at=time.time() + expires_in_seconds,
            created_by=created_by,
        )
        self._links[link.token] = link
        return link

    def resolve(self, token: str) -> ShareLink | None:
        link = self._links.get(token)
        if not link:
            return None
        if link.expires_at and time.time() > link.expires_at:
            del self._links[token]
            return None
        return link

    def revoke(self, token: str) -> bool:
        if token in self._links:
            del self._links[token]
            return True
        return False

    def revoke_all(self, dashboard_id: str) -> int:
        count = 0
        for token in list(self._links.keys()):
            if self._links[token].dashboard_id == dashboard_id:
                del self._links[token]
                count += 1
        return count

    def list_links(self, dashboard_id: str = "") -> list[ShareLink]:
        if dashboard_id:
            return [l for l in self._links.values() if l.dashboard_id == dashboard_id]
        return list(self._links.values())
