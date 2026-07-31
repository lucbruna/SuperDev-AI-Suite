from __future__ import annotations

import asyncio
import random
from typing import Any


class RollingDeploy:
    def __init__(self, batch_size: int = 2, wait_seconds: int = 5):
        self.batch_size = batch_size
        self.wait_seconds = wait_seconds

    async def execute(self, env: str, version: str, instances: list[str]) -> dict[str, Any]:
        results = []
        for i in range(0, len(instances), self.batch_size):
            batch = instances[i : i + self.batch_size]
            batch_results = []
            for inst in batch:
                await asyncio.sleep(self.wait_seconds)
                success = random.random() > 0.1
                batch_results.append({"instance": inst, "success": success, "version": version})
            results.extend(batch_results)
            if not all(r["success"] for r in batch_results):
                return {
                    "strategy": "rolling",
                    "status": "failed",
                    "results": results,
                    "failed_batch": i // self.batch_size,
                }
        return {"strategy": "rolling", "status": "completed", "results": results, "total_instances": len(instances)}


class BlueGreenDeploy:
    async def execute(self, env: str, version: str, active_slot: str = "blue") -> dict[str, Any]:
        new_slot = "green" if active_slot == "blue" else "blue"
        await asyncio.sleep(2)
        success = random.random() > 0.05
        if success:
            return {
                "strategy": "blue-green",
                "status": "completed",
                "previous_slot": active_slot,
                "new_active_slot": new_slot,
                "version": version,
            }
        return {"strategy": "blue-green", "status": "failed", "error": "Health check failed on new slot"}


class CanaryDeploy:
    def __init__(self, canary_percent: int = 10, promotion_minutes: int = 5):
        self.canary_percent = canary_percent
        self.promotion_minutes = promotion_minutes

    async def execute(self, env: str, version: str, total_instances: int = 10) -> dict[str, Any]:
        canary_count = max(1, total_instances * self.canary_percent // 100)
        await asyncio.sleep(2)
        canary_ok = random.random() > 0.08
        if not canary_ok:
            return {
                "strategy": "canary",
                "status": "rolled_back",
                "canary_count": canary_count,
                "error": "Canary health check failed",
            }
        await asyncio.sleep(self.promotion_minutes)
        return {
            "strategy": "canary",
            "status": "promoted",
            "canary_count": canary_count,
            "total_instances": total_instances,
            "version": version,
            "promotion_minutes": self.promotion_minutes,
        }


class RecreateDeploy:
    async def execute(self, env: str, version: str) -> dict[str, Any]:
        await asyncio.sleep(3)
        return {"strategy": "recreate", "status": "completed", "version": version, "downtime_seconds": 3}


def get_strategy(name: str):
    strategies = {
        "rolling": RollingDeploy,
        "blue-green": BlueGreenDeploy,
        "canary": CanaryDeploy,
        "recreate": RecreateDeploy,
    }
    cls = strategies.get(name)
    if not cls:
        raise ValueError(f"Unknown strategy: {name}. Options: {', '.join(strategies.keys())}")
    return cls()
