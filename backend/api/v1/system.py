"""FastAPI routes for system orchestrator integration.

Provides REST API endpoints to control and monitor the entire platform
through the Orchestrator, including boot, shutdown, health, metrics,
agents, workflows, plugins, and scheduling.
"""

from __future__ import annotations

from datetime import UTC
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.exceptions import AgentNotFoundException
from backend.schemas.agent import AgentExecuteRequest
from backend.services.agent_service import AgentService

# Shared serializer so /system/agents returns the exact same shape as
# /api/v1/agents (single source of truth for the agent contract).
from backend.api.v1.agents import _agent_response

router = APIRouter(
    tags=["system"],
    dependencies=[Depends(get_current_active_user)],
)

# Global orchestrator reference (set once during app initialization)
_orchestrator: Any = None


def set_orchestrator(orch: Any) -> None:
    """Set the global orchestrator instance for API access."""
    global _orchestrator
    _orchestrator = orch


def get_orchestrator() -> Any:
    """Get the global orchestrator instance."""
    if _orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialized",
        )
    return _orchestrator


# ─── Schemas ──────────────────────────────────────────────────────────────────


class BootRequest(BaseModel):
    config_path: str = ""
    safe_mode: bool = False
    skip_plugins: bool = False
    skip_ai: bool = False


class BootResponse(BaseModel):
    success: bool
    total_phases: int
    completed: int
    failed: list[str]
    total_time: float


class ExecuteRequest(AgentExecuteRequest):
    """Execute an agent task (shares the canonical AgentExecuteRequest contract)."""

    agent_id: str


class ScheduleRequest(BaseModel):
    name: str
    interval_seconds: float = 0
    cron_expr: str = ""
    task_type: str = "workflow"


# ─── System ───────────────────────────────────────────────────────────────────


@router.post("/boot", response_model=BootResponse)
async def boot_system(
    request: BootRequest = BootRequest(),
) -> Any:
    """Execute the full system boot sequence."""
    orch = get_orchestrator()
    from core.orchestrator.types import BootConfig

    config = BootConfig(
        safe_mode=request.safe_mode,
        skip_plugins=request.skip_plugins,
        skip_ai=request.skip_ai,
    )
    result = await orch.boot(boot_config=config)
    return BootResponse(**result)


@router.post("/shutdown")
async def shutdown_system() -> dict[str, Any]:
    """Gracefully shut down the entire platform."""
    orch = get_orchestrator()
    result = await orch.shutdown(timeout=30.0)
    return {"success": result.get("success", False)}


@router.get("/status")
async def system_status() -> dict[str, Any]:
    """Get complete system status information."""
    orch = get_orchestrator()
    return await orch.get_system_info()


@router.get("/health")
async def system_health() -> dict[str, Any]:
    """Get system health summary."""
    orch = get_orchestrator()
    return {
        "orchestrator": {
            "status": orch.status.value,
            "uptime": orch.uptime,
            "is_running": orch.is_running,
        },
        "services": orch.service_registry.get_summary(),
        "health": orch.health_monitor.get_summary(),
        "event_bus": orch.event_bus.get_statistics(),
    }


# ─── Agents ──────────────────────────────────────────────────────────────────
#
# Agent endpoints are DB-backed through AgentService — the same source of
# truth as /api/v1/agents — instead of the orchestrator's in-memory registry.


@router.get("/agents")
async def list_agents(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """List all registered AI agents (DB-backed)."""
    service = AgentService(db)
    agents, total = await service.list_agents(page=1, page_size=1000)
    return {
        "agents": [_agent_response(a) for a in agents],
        "statistics": {
            "total": total,
            "active": sum(1 for a in agents if a.is_active),
        },
    }


@router.get("/agents/{agent_id}")
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get details for a specific agent."""
    service = AgentService(db)
    try:
        agent = await service.get_agent(agent_id)
    except AgentNotFoundException:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return _agent_response(agent)


@router.post("/agents/{agent_id}/start")
async def start_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Start a specific agent (mark as active)."""
    service = AgentService(db)
    try:
        updated = await service.update_agent(agent_id, is_active=True)
    except AgentNotFoundException:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return _agent_response(updated)


@router.post("/agents/{agent_id}/stop")
async def stop_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Stop a specific agent (mark as inactive)."""
    service = AgentService(db)
    try:
        updated = await service.update_agent(agent_id, is_active=False)
    except AgentNotFoundException:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return _agent_response(updated)


@router.post("/agents/execute")
async def execute_agent(
    request: ExecuteRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Execute a task using a specific agent."""
    from backend.agents.execution import run_persisted_agent

    service = AgentService(db)
    try:
        agent = await service.get_agent(request.agent_id)
    except AgentNotFoundException:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")

    if not agent.is_active:
        raise HTTPException(status_code=400, detail="Agent is not active")

    return await run_persisted_agent(db, agent, request.task, request.context)


# ─── Workflows ───────────────────────────────────────────────────────────────


@router.post("/workflows")
async def create_workflow(config: dict[str, Any]) -> dict[str, Any]:
    """Create a new workflow."""
    orch = get_orchestrator()
    return await orch.workflow_bridge.create_workflow(config)


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a workflow."""
    orch = get_orchestrator()
    try:
        return await orch.workflow_bridge.execute_workflow(workflow_id, context)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/workflows")
async def list_workflows(status: str = "") -> dict[str, Any]:
    """List all workflows."""
    orch = get_orchestrator()
    return {
        "workflows": orch.workflow_bridge.list_workflows(status=status),
        "statistics": orch.workflow_bridge.get_statistics(),
    }


# ─── Scheduler ───────────────────────────────────────────────────────────────


@router.get("/scheduler/tasks")
async def list_scheduled_tasks() -> dict[str, Any]:
    """List all scheduled tasks."""
    orch = get_orchestrator()
    return {
        "tasks": orch.task_scheduler.list_tasks(),
        "statistics": orch.task_scheduler.get_statistics(),
    }


@router.post("/scheduler/run/{task_id}")
async def run_task(task_id: str) -> dict[str, Any]:
    """Run a specific scheduled task immediately."""
    orch = get_orchestrator()
    return await orch.task_scheduler.run_once(task_id)


# ─── Metrics ─────────────────────────────────────────────────────────────────


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """Get system-wide metrics."""
    orch = get_orchestrator()
    metrics = await orch.collect_metrics()
    return {
        "system": metrics.__dict__,
        "event_bus": orch.event_bus.get_statistics(),
        "recovery": orch.recovery_manager.get_failure_summary(),
        "scheduler": orch.task_scheduler.get_statistics(),
    }


# ─── Self-Test ────────────────────────────────────────────────────────────────


@router.get("/self-test")
async def self_test() -> dict[str, Any]:
    """Run system self-diagnostics: scanner resolution, scan execution, error handling."""
    import time

    from backend.api.v1.scanners import SCANNER_REGISTRY, _resolve_scanner_class, run_scanner, run_security

    results: list[dict[str, Any]] = []
    failures = 0

    def add_result(name: str, passed: bool, detail: str = "", data: Any = None) -> None:
        nonlocal failures
        if not passed:
            failures += 1
        results.append(
            {
                "test": name,
                "passed": passed,
                "detail": detail[:200],
                "data": data,
            }
        )

    # ── Test 1: Scanner resolution ────────────────────────────────────
    available = 0
    unavailable = 0
    for sid in SCANNER_REGISTRY:
        cls = _resolve_scanner_class(sid)
        if cls is not None:
            available += 1
        else:
            unavailable += 1
    add_result(
        "scanner_resolution",
        passed=available > 0,
        detail=f"{available} disponiveis, {unavailable} indisponiveis de {len(SCANNER_REGISTRY)} total",
        data={"total": len(SCANNER_REGISTRY), "available": available, "unavailable": unavailable},
    )

    # ── Test 2: Run filesystem scanner (lightweight) ──────────────────
    import os

    target = os.path.abspath("./backend")

    try:
        cls = _resolve_scanner_class("filesystem")
        if cls:
            t0 = time.time()
            result = await run_scanner("filesystem", cls, target, timeout=15)
            elapsed = round((time.time() - t0) * 1000, 2)
            add_result(
                "filesystem_scan",
                passed=not result.get("error", ""),
                detail=f"{result.get('total_findings', 0)} findings em {elapsed:.0f}ms | sev: {result.get('by_severity', {})}",
                data={
                    "findings": result.get("total_findings", 0),
                    "duration_ms": elapsed,
                    "by_severity": result.get("by_severity", {}),
                },
            )
        else:
            add_result("filesystem_scan", passed=False, detail="Scanner nao disponivel")
    except Exception as e:
        add_result("filesystem_scan", passed=False, detail=str(e)[:200])

    # ── Test 3: Run source_code scanner ───────────────────────────────
    try:
        cls = _resolve_scanner_class("source_code")
        if cls:
            result = await run_scanner("source_code", cls, target, timeout=30)
            sev = result.get("by_severity", {})
            add_result(
                "source_code_scan",
                passed=not result.get("error", ""),
                detail=f"{result.get('total_findings', 0)} findings | critical={sev.get('critical', 0)}, high={sev.get('high', 0)}",
                data={"findings": result.get("total_findings", 0), "by_severity": sev},
            )
        else:
            add_result("source_code_scan", passed=False, detail="Scanner nao disponivel")
    except Exception as e:
        add_result("source_code_scan", passed=False, detail=str(e)[:200])

    # ── Test 4: OWASP analyzer ────────────────────────────────────────
    try:
        cls = _resolve_scanner_class("owasp")
        if cls:
            result = await run_security("owasp", cls, target, timeout=30)
            sev = result.get("by_severity", {})
            add_result(
                "owasp_analysis",
                passed=not result.get("error", ""),
                detail=f"{result.get('total_findings', 0)} findings | critical={sev.get('critical', 0)}",
                data={"findings": result.get("total_findings", 0), "by_severity": sev},
            )
        else:
            add_result("owasp_analysis", passed=False, detail="OWASP analyzer nao disponivel")
    except Exception as e:
        add_result("owasp_analysis", passed=False, detail=str(e)[:200])

    # ── Test 5: Invalid scanner (404) ─────────────────────────────────
    cls = _resolve_scanner_class("nao_existe_123")
    add_result(
        "invalid_scanner_404",
        passed=cls is None,
        detail=f"Scanner inexistente retornou {'None (correto)' if cls is None else 'classe inesperada'}",
    )

    # ── Test 6: Builder resolution ────────────────────────────────────
    from backend.api.v1.builders import BUILDER_REGISTRY, _resolve_builder_class

    b_available = 0
    b_unavailable = 0
    for bid in BUILDER_REGISTRY:
        cls = _resolve_builder_class(bid)
        if cls is not None:
            b_available += 1
        else:
            b_unavailable += 1
    add_result(
        "builder_resolution",
        passed=b_available > 0,
        detail=f"{b_available} disponiveis, {b_unavailable} indisponiveis de {len(BUILDER_REGISTRY)} total",
        data={"total": len(BUILDER_REGISTRY), "available": b_available, "unavailable": b_unavailable},
    )

    # ── Test 7: Run backend builder (lightweight test) ────────────────
    try:
        cls = _resolve_builder_class("backend")
        if cls:
            from backend.api.v1.builders import BuildRequest, run_builder

            t0 = time.time()
            result = await run_builder(
                "backend",
                cls,
                BuildRequest(project_name="TestProj", include_docker=False, include_tests=False, include_ci=False),
            )
            elapsed = round((time.time() - t0) * 1000, 2)
            add_result(
                "backend_builder",
                passed=not result.get("error", ""),
                detail=f"{result.get('total_files', 0)} files generated in {elapsed:.0f}ms",
                data={"total_files": result.get("total_files", 0), "duration_ms": elapsed},
            )
        else:
            add_result("backend_builder", passed=False, detail="Builder backend nao disponivel")
    except Exception as e:
        add_result("backend_builder", passed=False, detail=str(e)[:200])

    # ── Summary ────────────────────────────────────────────────────────
    from datetime import datetime

    passed_count = sum(1 for r in results if r["passed"])
    return {
        "success": failures == 0,
        "timestamp": datetime.now(UTC).isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": failures,
        },
        "results": results,
    }
