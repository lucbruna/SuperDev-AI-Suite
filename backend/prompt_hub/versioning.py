from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any


class PromptVersionManager:
    def __init__(self):
        self._versions: dict[str, list[dict[str, Any]]] = {}

    def add_version(
        self, prompt_id: str, content: str, model: str, author: str = "", tags: list[str] | None = None
    ) -> dict[str, Any]:
        if prompt_id not in self._versions:
            self._versions[prompt_id] = []
        history = self._versions[prompt_id]
        version_number = len(history) + 1
        entry = {
            "prompt_id": prompt_id,
            "version": version_number,
            "content": content,
            "model": model,
            "author": author,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat(),
            "hash": str(uuid.uuid4().hex[:12]),
        }
        history.append(entry)
        return entry

    def get_version(self, prompt_id: str, version: int | None = None) -> dict[str, Any] | None:
        history = self._versions.get(prompt_id, [])
        if not history:
            return None
        if version is None:
            return history[-1]
        for v in history:
            if v["version"] == version:
                return v
        return None

    def list_versions(self, prompt_id: str) -> list[dict[str, Any]]:
        return self._versions.get(prompt_id, [])

    def promote_version(self, prompt_id: str, version: int) -> dict[str, Any] | None:
        entry = self.get_version(prompt_id, version)
        if not entry:
            return None
        entry["promoted_at"] = datetime.utcnow().isoformat()
        entry["is_production"] = True
        return entry

    def compare_versions(self, prompt_id: str, v1: int, v2: int) -> dict[str, Any] | None:
        a = self.get_version(prompt_id, v1)
        b = self.get_version(prompt_id, v2)
        if not a or not b:
            return None
        import difflib

        diff = list(
            difflib.unified_diff(
                a["content"].splitlines(keepends=True),
                b["content"].splitlines(keepends=True),
                fromfile=f"v{v1}",
                tofile=f"v{v2}",
            )
        )
        return {
            "prompt_id": prompt_id,
            "version_a": v1,
            "version_b": v2,
            "diff": "".join(diff),
            "lines_changed": len([l for l in diff if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]),
        }

    def get_stats(self, prompt_id: str) -> dict[str, Any]:
        history = self._versions.get(prompt_id, [])
        if not history:
            return {"total_versions": 0, "latest_version": 0, "first_created": None}
        return {
            "total_versions": len(history),
            "latest_version": history[-1]["version"],
            "first_created": history[0]["created_at"],
            "last_updated": history[-1]["created_at"],
            "authors": list({v["author"] for v in history if v["author"]}),
        }
