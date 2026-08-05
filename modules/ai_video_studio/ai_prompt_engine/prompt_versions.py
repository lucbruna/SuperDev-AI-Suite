"""Prompt versions — version history for prompt iterations."""
from __future__ import annotations

import time
import uuid
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError


class PromptVersions:
    """Tracks versioned iterations of a prompt."""

    def __init__(self, max_versions: int = 20) -> None:
        self._versions: dict[str, list[dict[str, Any]]] = {}
        self.max_versions = max_versions

    def create(self, prompt_id: str, prompt: str, author: str = "system", **meta: Any) -> dict[str, Any]:
        if not prompt.strip():
            raise ValidationError("Prompt cannot be empty", field="prompt")
        version = {
            "version": len(self._versions.get(prompt_id, [])) + 1,
            "id": str(uuid.uuid4()),
            "prompt": prompt,
            "author": author,
            "created_at": time.time(),
            **meta,
        }
        versions = self._versions.setdefault(prompt_id, [])
        versions.append(version)
        if len(versions) > self.max_versions:
            self._versions[prompt_id] = versions[-self.max_versions :]
        return version

    def get(self, prompt_id: str, version: int | None = None) -> dict[str, Any] | None:
        versions = self._versions.get(prompt_id, [])
        if not versions:
            return None
        if version is None:
            return versions[-1]
        if version < 1 or version > len(versions):
            return None
        return versions[version - 1]

    def list(self, prompt_id: str) -> list[dict[str, Any]]:
        return list(self._versions.get(prompt_id, []))

    def diff(self, prompt_id: str, v1: int, v2: int) -> dict[str, Any]:
        a = self.get(prompt_id, v1)
        b = self.get(prompt_id, v2)
        if a is None or b is None:
            raise ValidationError("Version not found", field="version")
        a_set = set(a["prompt"].split())
        b_set = set(b["prompt"].split())
        return {
            "added": sorted(b_set - a_set),
            "removed": sorted(a_set - b_set),
            "from_version": v1,
            "to_version": v2,
        }

    def rollback(self, prompt_id: str, version: int) -> dict[str, Any]:
        target = self.get(prompt_id, version)
        if target is None:
            raise ValidationError("Version not found", field="version")
        latest = self.get(prompt_id)
        if latest and latest["version"] != target["version"]:
            return self.create(prompt_id, target["prompt"], author="rollback")
        return target


_prompt_versions: PromptVersions | None = None


def get_prompt_versions() -> PromptVersions:
    global _prompt_versions
    if _prompt_versions is None:
        _prompt_versions = PromptVersions()
    return _prompt_versions
