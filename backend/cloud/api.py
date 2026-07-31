from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

# Optional imports — runtime_engine modules may not be installed
# Cloud features are gracefully disabled when the engine is unavailable
try:
    from runtime_engine.cloud.vm_orchestrator import VMOrchestrator
    _orchestrator = VMOrchestrator(provider="aws")
except ImportError:
    logger.warning("runtime_engine.cloud.vm_orchestrator not available — VM features disabled")
    _orchestrator = None

try:
    from runtime_engine.cloud.container_pool import ContainerPool
    _pool = ContainerPool()
    _has_pool = True
except ImportError:
    logger.warning("runtime_engine.cloud.container_pool not available — container pool disabled")
    _pool = None
    _has_pool = False

try:
    from runtime_engine.cloud.browser import BrowserSession
    _browser = BrowserSession()
except ImportError:
    logger.warning("runtime_engine.cloud.browser not available — browser sessions disabled")
    _browser = None

try:
    from runtime_engine.cloud.snapshot import SnapshotManager
    _snapshots = SnapshotManager()
except ImportError:
    logger.warning("runtime_engine.cloud.snapshot not available — snapshot features disabled")
    _snapshots = None

router = APIRouter(prefix="/cloud", tags=["cloud"])


@router.on_event("startup")
async def _init_pool():
    if _has_pool and _pool is not None:
        await _pool.start()


@router.post("/vms")
async def create_vm(name: str, cpu: int = 2, memory: int = 4, disk: int = 20):
    vm = await _orchestrator.create_vm(name, {"cpu": cpu, "memory_gb": memory, "disk_gb": disk})
    return vm


@router.get("/vms")
async def list_vms(status: str | None = None):
    vms = await _orchestrator.list_vms(status)
    return {"vms": vms, "total": len(vms)}


@router.get("/vms/{vm_id}")
async def get_vm(vm_id: str):
    vm = await _orchestrator.get_vm(vm_id)
    if not vm:
        raise HTTPException(status_code=404, detail="VM not found")
    return vm


@router.post("/vms/{vm_id}/stop")
async def stop_vm(vm_id: str):
    result = await _orchestrator.stop_vm(vm_id)
    if not result:
        raise HTTPException(status_code=404, detail="VM not found or already stopped")
    return {"status": "stopped"}


@router.post("/vms/{vm_id}/start")
async def start_vm(vm_id: str):
    result = await _orchestrator.start_vm(vm_id)
    if not result:
        raise HTTPException(status_code=404, detail="VM not found")
    return {"status": "started"}


@router.post("/vms/{vm_id}/destroy")
async def destroy_vm(vm_id: str):
    result = await _orchestrator.destroy_vm(vm_id)
    if not result:
        raise HTTPException(status_code=404, detail="VM not found")
    return {"status": "destroyed"}


@router.post("/vms/{vm_id}/exec")
async def exec_on_vm(vm_id: str, command: str):
    return await _orchestrator.execute_command(vm_id, command)


@router.get("/pool")
async def get_pool_stats():
    return await _pool.get_stats()


@router.post("/pool/scale-up")
async def scale_up(count: int = 3):
    added = await _pool.scale_up(count)
    return {"added": added, "total": (await _pool.get_stats())["total"]}


@router.post("/pool/scale-down")
async def scale_down(count: int = 3):
    removed = await _pool.scale_down(count)
    return {"removed": removed, "total": (await _pool.get_stats())["total"]}


@router.post("/browser/launch")
async def launch_browser(url: str = "about:blank"):
    session = await _browser.launch(url)
    return session


@router.post("/browser/{session_id}/navigate")
async def navigate(session_id: str, url: str):
    return await _browser.navigate(session_id, url)


@router.get("/browser/{session_id}/screenshot")
async def screenshot(session_id: str):
    return await _browser.screenshot(session_id)


@router.post("/browser/{session_id}/close")
async def close_browser(session_id: str):
    result = await _browser.close(session_id)
    return {"closed": result}


@router.post("/snapshots")
async def create_snapshot(vm_id: str, name: str = ""):
    return await _snapshots.create(vm_id, name)


@router.get("/snapshots")
async def list_snapshots(vm_id: str | None = None):
    snaps = await _snapshots.list(vm_id)
    return {"snapshots": snaps, "total": len(snaps)}


@router.get("/stats")
async def get_stats():
    vm_stats = await _orchestrator.get_vm_stats()
    pool_stats = await _pool.get_stats()
    snap_stats = await _snapshots.get_stats()
    return {**vm_stats, "pool": pool_stats, "snapshots": snap_stats}