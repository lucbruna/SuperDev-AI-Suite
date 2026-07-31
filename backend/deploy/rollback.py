from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any


class RollbackManager:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self._history: dict[str, list[dict[str, Any]]] = {}

    def record_deploy(self, env: str, version: str, strategy: str, status: str, snapshot: dict[str, Any] | None = None) -> str:
        entry_id = f"rb_{uuid.uuid4().hex[:12]}"
        if env not in self._history:
            self._history[env] = []
        self._history[env].append({
            "id": entry_id,
            "env": env,
            "version": version,
            "strategy": strategy,
            "status": status,
            "snapshot": snapshot or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(self._history[env]) > self.max_history:
            self._history[env] = self._history[env][-self.max_history:]
        return entry_id

    async def rollback(self, env: str, target_version: str | None = None) -> dict[str, Any]:
        history = self._history.get(env, [])
        if not history:
            return {"success": False, "error": f"No deploy history for {env}"}

        if target_version:
            target = next((h for h in reversed(history) if h["version"] == target_version), None)
            if not target:
                return {"success": False, "error": f"Version {target_version} not found in {env} history"}
        else:
            target = history[-1]

        rollback_id = f"rollback_{uuid.uuid4().hex[:12]}"
        return {
            "id": rollback_id,
            "env": env,
            "from_version": history[-1]["version"] if history else "unknown",
            "to_version": target["version"],
            "status": "completed",
            "snapshot_restored": bool(target.get("snapshot")),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_history(self, env: str | None = None) -> dict[str, list[dict[str, Any]]]:
        if env:
            return {env: self._history.get(env, [])}
        return dict(self._history)

    async def auto_rollback_if_needed(self, env: str, health_check_result: dict[str, Any]) -> dict[str, Any] | None:
        if not health_check_result.get("healthy", True):
            return await self.rollback(env)
        return None

    async def schedule_rollback(self, env: str, delay_seconds: int = 30) -> str:
        import asyncio
        task_id = f"auto_rb_{uuid.uuid4().hex[:8]}"
        asyncio.create_task(self._delayed_rollback(task_id, env, delay_seconds))
        return task_id

    async def _delayed_rollback(self, task_id: str, env: str, delay: int) -> None:
        await asyncio.sleep(delay)
        await self.rollback(env)
