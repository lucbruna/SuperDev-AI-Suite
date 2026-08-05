"""Tests for Volume 10 — Suite Integration (AI Video Studio ↔ SuperDev platform).

The suite platform packages live in the same repo (``SuperDev.integration``,
``SuperDev.security``, ``SuperDev.monitoring``, ``SuperDev.workflow``,
``backend.auth.jwt``), so most adapters run against the real platform.
Adapters must always answer without raising and fall back locally.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from modules.ai_video_studio.suite_integration import SUITE_MANIFEST, get_suite_bridge
from modules.ai_video_studio.suite_integration.adapters import get_adapters
from modules.ai_video_studio.suite_integration.adapters.security_adapter import (
    SecurityAdapter,
)


# ── Manifest ────────────────────────────────────────────────────
def test_manifest_declares_platform_contract():
    manifest = SUITE_MANIFEST.to_dict()
    assert manifest["module"] == "ai_video_studio"
    assert manifest["version"] == "1.0.0"
    assert "auth" in manifest["consumes"]
    assert "security.ssrf" in manifest["consumes"]
    assert "speaking_avatar" in manifest["provides"]
    assert "suite_bridge" in manifest["services"]


# ── Bridge discovery ────────────────────────────────────────────
def test_bridge_check_discovers_platform():
    check = get_suite_bridge().check()
    assert check["module"] == "ai_video_studio"
    assert check["native"] is True  # SuperDev package reachable
    assert len(check["adapters"]) == 6
    # Real platform components must be importable from this repo.
    assert check["platform_modules"]["security"] is True
    assert check["platform_modules"]["integration"] is True
    assert check["platform_modules"]["workflow"] is True
    assert check["platform_modules"]["observability"] is True
    # plugin_platform exists but cannot import (missing top-level `core`) → False.
    assert check["platform_modules"]["plugins"] is False


def test_all_adapters_answer_status():
    for adapter in get_adapters():
        status = adapter.status()
        assert status["name"] == adapter.name
        assert isinstance(status["available"], bool)
        assert isinstance(status["actions"], list)


# ── Security adapter (SSRF) ─────────────────────────────────────
def test_security_blocks_private_urls():
    adapter = SecurityAdapter()
    assert adapter.validate_url("http://169.254.169.254/latest/meta-data")["safe"] is False
    assert adapter.validate_url("http://127.0.0.1/admin")["safe"] is False
    assert adapter.validate_url("http://192.168.1.10")["safe"] is False
    assert adapter.validate_url("ftp://example.com/file")["safe"] is False


def test_security_allows_public_url():
    # Public IP literal → no DNS lookup, fully hermetic.
    result = SecurityAdapter().validate_url("https://8.8.8.8")
    assert result["safe"] is True


def test_security_local_fallback_matches_policy():
    # Simulate an environment where the suite module is unreachable.
    adapter = SecurityAdapter()
    adapter.platform_module = "no.such.platform.module"
    assert adapter.available() is False
    assert adapter.validate_url("http://10.0.0.5/secret")["safe"] is False
    assert adapter.validate_url("https://8.8.8.8")["safe"] is True
    assert adapter.validate_url("ftp://x")["safe"] is False


def test_security_is_internal_host():
    adapter = SecurityAdapter()
    assert adapter.is_internal_host("169.254.169.254")["internal"] is True
    assert adapter.is_internal_host("8.8.8.8")["internal"] is False  # no DNS needed


# ── Auth adapter (platform JWT) ─────────────────────────────────
async def test_auth_rejects_missing_token():
    result = await get_suite_bridge().verify_token(None)
    assert result["ok"] is False
    assert result["reason"] == "missing_token"


async def test_auth_rejects_garbage_token():
    result = await get_suite_bridge().verify_token("not.a.real.jwt")
    assert result["ok"] is False
    assert result["platform"] is True  # platform JWT manager answered


# ── Integration adapter ─────────────────────────────────────────
def test_integration_registers_with_platform():
    adapter = get_adapters()[0]
    assert adapter.name == "integration"
    result = adapter.register_with_platform()
    assert result["registered"] is True
    assert result["integration_id"] == "ai_video_studio"
    assert result["engine_status"]["started"] is True


# ── Workflow adapter ────────────────────────────────────────────
def test_workflow_registers_pipeline():
    adapter = [a for a in get_adapters() if a.name == "workflow"][0]
    result = adapter.register_pipeline()
    assert result["registered"] is True
    assert result["workflow_id"]
    assert result["steps"] == ["plan", "generate", "render", "export"]


# ── Plugin adapter (local registry fallback) ────────────────────
def test_plugin_uses_local_registry_when_platform_broken(monkeypatch):
    # Simulate an unavailable platform instead of depending on repo state.
    from modules.ai_video_studio.suite_integration.adapters import plugin_adapter as pa

    adapter = [a for a in get_adapters() if a.name == "plugins"][0]
    monkeypatch.setattr(adapter, "available", lambda: False)
    monkeypatch.setattr(pa, "import_optional", lambda *a, **k: None)
    result = adapter.register_plugins()
    assert result["platform"] is False
    assert result["registered"] == 8
    assert "speaking_avatar" in result["plugins"]


# ── Bridge registration + metrics ───────────────────────────────
def test_bridge_register_with_platform_aggregates():
    result = get_suite_bridge().register_with_platform()
    assert set(result) == {"integration", "workflow", "plugins"}
    assert result["integration"]["registered"] is True
    assert result["workflow"]["registered"] is True


def test_bridge_record_metric():
    result = get_suite_bridge().record_metric("speaks", 1, profile="biz_maya")
    assert result["recorded"].startswith("speaks:")
    assert result["total"] >= 1


# ── API ─────────────────────────────────────────────────────────
def test_api_suite_endpoints():
    client = TestClient(_create_app())
    base = "/api/v1/video-studio/suite-integration"

    resp = client.get(f"{base}/status")
    assert resp.status_code == 200
    assert len(resp.json()["data"]["adapters"]) == 6

    resp = client.get(f"{base}/manifest")
    assert resp.status_code == 200
    assert "consumes" in resp.json()["data"]

    resp = client.post(f"{base}/register")
    assert resp.status_code == 200
    assert resp.json()["data"]["integration"]["registered"] is True

    resp = client.post(f"{base}/validate-url", json={"url": "http://169.254.169.254/x"})
    assert resp.status_code == 400  # SSRF policy rejects metadata endpoint

    resp = client.post(f"{base}/validate-url", json={"url": "https://8.8.8.8"})
    assert resp.status_code == 200
    assert resp.json()["data"]["safe"] is True

    resp = client.post(f"{base}/verify-token", json={"token": "garbage"})
    assert resp.status_code == 401


# ── Studio integration manager exposes the bridge ───────────────
def test_integration_manager_registers_suite_bridge():
    from modules.ai_video_studio.integration.integration_manager import (
        get_integration_manager,
    )

    services = get_integration_manager().register_studio_services()
    assert services >= 7
    names = [s["name"] for s in get_integration_manager().registry.list_services()]
    assert "suite_bridge" in names


def _create_app():
    from modules.ai_video_studio.api.main import create_app

    return create_app()
