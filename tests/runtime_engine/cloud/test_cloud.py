import pytest
from runtime_engine.cloud.vm_orchestrator import VMOrchestrator
from runtime_engine.cloud.container_pool import ContainerPool
from runtime_engine.cloud.browser import BrowserSession
from runtime_engine.cloud.snapshot import SnapshotManager


@pytest.mark.asyncio
async def test_vm_orchestrator_create_and_list():
    orch = VMOrchestrator(provider="aws")
    vm = await orch.create_vm("test-vm", {"cpu": 4, "memory_gb": 8})
    assert vm["name"] == "test-vm"
    assert vm["provider"] == "aws"
    assert vm["status"] == "provisioning"

    vms = await orch.list_vms()
    assert len(vms) == 1


@pytest.mark.asyncio
async def test_vm_lifecycle():
    orch = VMOrchestrator(provider="aws")
    vm = await orch.create_vm("lifecycle-test")
    assert vm["status"] == "provisioning"

    await orch._provision_vm(vm["id"])
    started = await orch.get_vm(vm["id"])
    assert started["status"] == "running"

    stopped = await orch.stop_vm(vm["id"])
    assert stopped is True
    assert (await orch.get_vm(vm["id"]))["status"] == "stopped"

    restarted = await orch.start_vm(vm["id"])
    assert restarted is True
    assert (await orch.get_vm(vm["id"]))["status"] == "running"

    destroyed = await orch.destroy_vm(vm["id"])
    assert destroyed is True
    assert await orch.get_vm(vm["id"]) is None


@pytest.mark.asyncio
async def test_vm_attach_detach_agent():
    orch = VMOrchestrator()
    vm = await orch.create_vm("agent-vm")
    await orch._provision_vm(vm["id"])

    attached = await orch.attach_agent(vm["id"], "agent_123")
    assert attached is True
    assert (await orch.get_vm(vm["id"]))["status"] == "occupied"

    detached = await orch.detach_agent(vm["id"])
    assert detached is True
    assert (await orch.get_vm(vm["id"]))["status"] == "running"


@pytest.mark.asyncio
async def test_vm_execute_command():
    orch = VMOrchestrator()
    vm = await orch.create_vm("exec-vm")
    await orch._provision_vm(vm["id"])

    result = await orch.execute_command(vm["id"], "ls -la")
    assert result["exit_code"] == 0
    assert "ls -la" in result["stdout"]


@pytest.mark.asyncio
async def test_vm_stats():
    orch = VMOrchestrator()
    await orch.create_vm("vm-1")
    await orch.create_vm("vm-2")
    stats = await orch.get_vm_stats()
    assert stats["total"] == 2
    assert stats["provider"] == "aws"


@pytest.mark.asyncio
async def test_container_pool_start():
    pool = ContainerPool(min_size=2)
    await pool.start()
    stats = await pool.get_stats()
    assert stats["total"] == 2
    assert stats["idle"] == 2


@pytest.mark.asyncio
async def test_container_pool_acquire_release():
    pool = ContainerPool(min_size=2)
    await pool.start()

    c1 = await pool.acquire()
    assert c1 is not None
    assert c1["status"] == "busy"

    released = await pool.release(c1["id"])
    assert released is True

    c1_again = await pool.acquire()
    assert c1_again is not None
    assert c1_again["id"] == c1["id"]
    assert c1_again["status"] == "busy"


@pytest.mark.asyncio
async def test_container_pool_scale():
    pool = ContainerPool(min_size=1, max_size=10)
    await pool.start()

    added = await pool.scale_up(5)
    assert added >= 5
    stats = await pool.get_stats()
    assert stats["total"] >= 6

    removed = await pool.scale_down(3)
    assert removed == 3
    stats = await pool.get_stats()
    assert stats["total"] >= 3


@pytest.mark.asyncio
async def test_browser_launch_and_navigate():
    browser = BrowserSession()
    session = await browser.launch("https://example.com")
    assert session["status"] == "launched"
    assert session["url"] == "https://example.com"

    result = await browser.navigate(session["id"], "https://other.com")
    assert result["status"] == "navigated"

    sessions = await browser.list_sessions()
    assert len(sessions) == 1


@pytest.mark.asyncio
async def test_browser_screenshot_and_close():
    browser = BrowserSession()
    session = await browser.launch()

    ss = await browser.screenshot(session["id"])
    assert "screenshot" in ss
    assert ss["screenshot"].startswith("data:image")

    closed = await browser.close(session["id"])
    assert closed is True
    assert len(await browser.list_sessions()) == 0


@pytest.mark.asyncio
async def test_browser_interaction():
    browser = BrowserSession()
    session = await browser.launch()

    eval_res = await browser.evaluate(session["id"], "document.title")
    assert "result" in eval_res

    html = await browser.get_html(session["id"])
    assert "Mock content" in html["html"]

    click = await browser.click(session["id"], "#submit")
    assert click["status"] == "clicked"

    typed = await browser.type_text(session["id"], "#name", "John")
    assert typed["status"] == "typed"


@pytest.mark.asyncio
async def test_snapshot_create_and_list():
    snapman = SnapshotManager()
    snap = await snapman.create("vm_123", "backup-1", {"owner": "admin"})
    assert snap["status"] == "completed"
    assert snap["vm_id"] == "vm_123"
    assert snap["metadata"]["owner"] == "admin"

    snaps = await snapman.list("vm_123")
    assert len(snaps) == 1

    all_snaps = await snapman.list()
    assert len(all_snaps) == 1


@pytest.mark.asyncio
async def test_snapshot_restore_and_delete():
    snapman = SnapshotManager()
    snap = await snapman.create("vm_123", "pre-update")

    restored = await snapman.restore(snap["id"], "vm_456")
    assert restored["status"] == "restored"
    assert restored["target_vm_id"] == "vm_456"

    deleted = await snapman.delete(snap["id"])
    assert deleted is True
    assert await snapman.get(snap["id"]) is None


@pytest.mark.asyncio
async def test_snapshot_clone_vm():
    snapman = SnapshotManager()
    snap = await snapman.create("vm_123", "snap-base")
    cloned = await snapman.clone_vm(snap["id"], "cloned-vm")
    assert cloned["status"] == "created"
    assert cloned["name"] == "cloned-vm"
    assert cloned["source_snapshot"] == snap["id"]


@pytest.mark.asyncio
async def test_snapshot_stats():
    snapman = SnapshotManager()
    await snapman.create("vm_1", "snap-a")
    await snapman.create("vm_2", "snap-b")
    await snapman.create("vm_1", "snap-c")
    stats = await snapman.get_stats()
    assert stats["total_snapshots"] == 3