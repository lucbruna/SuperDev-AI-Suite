from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/deploy", tags=["deploy"])

_environments: dict[str, dict[str, Any]] = {
    "development": {"status": "idle", "url": "http://dev.superdev.ai", "last_deploy": None},
    "staging": {"status": "idle", "url": "http://staging.superdev.ai", "last_deploy": None},
    "production": {"status": "idle", "url": "https://superdev.ai", "last_deploy": None},
}

_deployments: dict[str, dict[str, Any]] = {}


class DeployEngine:
    def __init__(self):
        self._running: dict[str, asyncio.Task] = {}

    async def deploy(self, env: str, version: str, strategy: str = "rolling") -> dict[str, Any]:
        if env not in _environments:
            raise HTTPException(status_code=400, detail=f"Unknown environment: {env}")
        if _environments[env]["status"] == "deploying":
            raise HTTPException(status_code=409, detail=f"Deploy already in progress for {env}")

        deploy_id = f"dep_{uuid.uuid4().hex[:12]}"
        _environments[env]["status"] = "deploying"

        pipeline = self._build_pipeline(env, version, strategy)
        _deployments[deploy_id] = {
            "id": deploy_id,
            "environment": env,
            "version": version,
            "strategy": strategy,
            "status": "running",
            "pipeline": pipeline,
            "current_step": 0,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }

        task = asyncio.create_task(self._execute_pipeline(deploy_id, env))
        self._running[deploy_id] = task
        return _deployments[deploy_id]

    def _build_pipeline(self, env: str, version: str, strategy: str) -> list[dict[str, Any]]:
        steps = [
            {"name": "build", "description": "Build container image", "estimated_seconds": 60},
            {"name": "test", "description": "Run integration tests", "estimated_seconds": 30},
        ]
        if env == "production":
            steps.append({"name": "canary", "description": "Canary deploy (10% traffic)", "estimated_seconds": 120})
            steps.append({"name": "health_check", "description": "Health check verification", "estimated_seconds": 30})
        if strategy == "blue-green":
            steps.append({"name": "blue_green_switch", "description": "Switch traffic to new version", "estimated_seconds": 10})
        steps.append({"name": "smoke_test", "description": "Smoke tests on live environment", "estimated_seconds": 30})
        if env == "production":
            steps.append({"name": "monitor", "description": "Monitoring window (5min)", "estimated_seconds": 300})
        steps.append({"name": "complete", "description": "Deploy finalized", "estimated_seconds": 0})
        return steps

    async def _execute_pipeline(self, deploy_id: str, env: str) -> None:
        dep = _deployments[deploy_id]
        steps = dep["pipeline"]
        for i, step in enumerate(steps):
            dep["current_step"] = i + 1
            dep["status"] = f"step:{step['name']}"
            await asyncio.sleep(step["estimated_seconds"] / 10)
        dep["status"] = "completed"
        dep["completed_at"] = datetime.utcnow().isoformat()
        _environments[env]["status"] = "idle"
        _environments[env]["last_deploy"] = dep["started_at"]
        self._running.pop(deploy_id, None)

    async def rollback(self, env: str) -> dict[str, Any]:
        if env not in _environments:
            raise HTTPException(status_code=400, detail=f"Unknown environment: {env}")
        deploy_id = f"rollback_{uuid.uuid4().hex[:8]}"
        _deployments[deploy_id] = {
            "id": deploy_id,
            "environment": env,
            "version": "previous",
            "strategy": "immediate",
            "status": "completed",
            "pipeline": [{"name": "rollback", "description": "Reverting to previous version", "estimated_seconds": 30}],
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
        }
        _environments[env]["status"] = "idle"
        return _deployments[deploy_id]


_engine = DeployEngine()


@router.post("/{env}")
async def deploy(env: str, version: str = "latest", strategy: str = "rolling"):
    return await _engine.deploy(env, version, strategy)


@router.post("/{env}/rollback")
async def rollback(env: str):
    return await _engine.rollback(env)


@router.get("/environments")
async def list_environments():
    return {"environments": [{"name": k, **v} for k, v in _environments.items()]}


@router.get("/history")
async def deploy_history(limit: int = 20):
    sorted_deps = sorted(_deployments.values(), key=lambda d: d.get("started_at", ""), reverse=True)
    return {"deployments": sorted_deps[:limit], "total": len(_deployments)}


@router.get("/{deploy_id}")
async def get_deploy(deploy_id: str):
    dep = _deployments.get(deploy_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Deploy not found")
    return dep


@router.get("/strategies")
async def list_strategies():
    return {"strategies": ["rolling", "blue-green", "canary", "immediate"]}