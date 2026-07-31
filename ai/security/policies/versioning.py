"""Policy versioning."""
from __future__ import annotations

import time
import uuid
from typing import Any


class PolicyVersion:
    def __init__(self, version: int, policy_id: str, content: dict[str, Any], author: str = "") -> None:
        self.version_id = str(uuid.uuid4())[:8]
        self.version = version
        self.policy_id = policy_id
        self.content = content
        self.author = author
        self.created_at = time.time()
        self.status = "draft"

class PolicyVersionManager:
    def __init__(self) -> None:
        self._versions: dict[str, PolicyVersion] = {}
        self._policy_versions: dict[str, list[str]] = {}
    def create_version(self, policy_id: str, content: dict[str, Any], author: str = "") -> PolicyVersion:
        current_versions = self._policy_versions.get(policy_id, [])
        version_num = len(current_versions) + 1
        version = PolicyVersion(version_num, policy_id, content, author)
        self._versions[version.version_id] = version
        self._policy_versions.setdefault(policy_id, []).append(version.version_id)
        return version
    def get_version(self, version_id: str) -> dict[str, Any] | None:
        v = self._versions.get(version_id)
        if v:
            return {"id": v.version_id, "version": v.version, "policy_id": v.policy_id, "author": v.author, "status": v.status, "created_at": v.created_at}
        return None
    def get_latest(self, policy_id: str) -> dict[str, Any] | None:
        versions = self._policy_versions.get(policy_id, [])
        if versions:
            return self.get_version(versions[-1])
        return None
    def list_versions(self, policy_id: str) -> list[dict[str, Any]]:
        versions = self._policy_versions.get(policy_id, [])
        results: list[dict[str, Any]] = []
        for v in versions:
            version = self.get_version(v)
            if version:
                results.append(version)
        return results
    def approve(self, version_id: str) -> bool:
        v = self._versions.get(version_id)
        if v:
            v.status = "approved"
            return True
        return False
    def rollback(self, policy_id: str, target_version: int) -> str | None:
        versions = self._policy_versions.get(policy_id, [])
        for vid in versions:
            v = self._versions.get(vid)
            if v and v.version == target_version:
                v.status = "active"
                return vid
        return None
