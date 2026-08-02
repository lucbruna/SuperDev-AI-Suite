"""Market publisher — submissions of skill definitions to the marketplace."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_marketplace import get_skill_marketplace
from modules.ai_video_studio.skills.skill_registry import SkillDefinition


class MarketPublisher:
    """Collects skill submissions and forwards approved ones to the catalog.

    A submission carries the definition, an author and a lifecycle status
    (``submitted`` → ``approved``/``rejected``). Approving publishes the
    entry into the shared marketplace catalog.
    """

    def __init__(self) -> None:
        self._marketplace = get_skill_marketplace()
        self._submissions: dict[str, dict[str, Any]] = {}

    def submit(
        self,
        definition: SkillDefinition,
        *,
        author: str = "unknown",
    ) -> dict[str, Any]:
        if self._submissions.get(definition.id, {}).get("status") == "approved":
            return {"skill_id": definition.id, "status": "approved", "submitted": False}
        self._submissions[definition.id] = {
            "skill_id": definition.id,
            "version": definition.version,
            "author": author,
            "definition": definition,
            "status": "submitted",
        }
        return {"skill_id": definition.id, "status": "submitted", "submitted": True}

    def get(self, skill_id: str) -> dict[str, Any] | None:
        return self._submissions.get(skill_id)

    def approve(self, skill_id: str) -> dict[str, Any]:
        submission = self._submissions.get(skill_id)
        if submission is None:
            return {"skill_id": skill_id, "status": "missing"}
        definition = submission["definition"]
        self._marketplace.publish_definition(definition)
        submission["status"] = "approved"
        return {"skill_id": skill_id, "status": "approved", "version": definition.version}

    def reject(self, skill_id: str, *, reason: str = "not reviewed") -> dict[str, Any]:
        submission = self._submissions.get(skill_id)
        if submission is None:
            return {"skill_id": skill_id, "status": "missing"}
        submission["status"] = "rejected"
        submission["reason"] = reason
        return {"skill_id": skill_id, "status": "rejected", "reason": reason}

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        items = self._submissions.values()
        if status:
            items = (s for s in items if s["status"] == status)
        return [
            {
                "skill_id": s["skill_id"],
                "version": s["version"],
                "author": s["author"],
                "status": s["status"],
            }
            for s in sorted(items, key=lambda s: s["skill_id"])
        ]
