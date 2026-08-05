"""Tests for Volume 10 — Global Suite Integration domain connectors.

Every connector must answer ``status()``/``capabilities()``/``execute()``
without raising, and produce JSON-serializable results. Video generators
return ``video_brief`` objects consumable by the studio pipelines.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from modules.ai_video_studio.integration.connectors_registry import (
    connector_count,
    get_connectors,
)


def _connector(domain: str):
    return get_connectors()[domain]


# ── Registration ─────────────────────────────────────────────────
def test_all_connectors_register_and_answer_status():
    connectors = get_connectors()
    assert connector_count() == 17
    assert len(connectors) == 17
    for domain, connector in connectors.items():
        assert connector is not None, domain
        status = connector.status()
        assert status["domain"] == domain
        assert isinstance(status["actions"], list)
        assert connector.capabilities()["domain"] == domain


def test_execute_unknown_action_returns_error():
    assert _connector("erp").execute("no_such_action")["ok"] is False


# ── Enterprise AI ────────────────────────────────────────────────
def test_enterprise_ai_route_and_reason():
    connector = _connector("enterprise_ai")
    routed = connector.execute("route_prompt", {"prompt": "write a script", "task": "script"})
    assert routed["ok"] is True and routed["provider"]
    reasoned = connector.execute("reason", {"question": "Should we render at 4K?", "evidence": ["gpu"]})
    assert reasoned["ok"] is True and reasoned["steps"]

    embedded = connector.execute("embed", {"text": "hello world"})
    assert len(embedded["vector"]) == 64
    assert connector.execute("vector_search", {"query": "hello"})["ok"] is True
    connector.execute("ingest_knowledge", {"fact": "The studio renders MP4 by default"})
    hits = connector.execute("query_knowledge", {"question": "renders"})
    assert hits["count"] == 1


# ── Agriculture ──────────────────────────────────────────────────
def test_agriculture_generates_briefs():
    connector = _connector("agriculture")
    brief = connector.execute("crop_video", {"crop": "soybean", "stage": "growth"})
    assert brief["ok"] is True
    assert brief["type"] == "video_brief"
    assert brief["domain"] == "agriculture"
    assert brief["scenes"] >= 3

    report = connector.execute("harvest_report", {"crop": "corn"})
    assert report["meta"]["stats"]["avg_yield_t_ha"] > 0


# ── ERP / CRM / HR / Finance / BI ────────────────────────────────
def test_erp_generates_briefs():
    brief = _connector("erp").execute("invoice_video", {"invoice_id": "INV-1", "amount": 1000})
    assert brief["type"] == "video_brief" and brief["domain"] == "erp"
    assert "INV-1" in brief["narration"]


def test_crm_generates_briefs():
    ad = _connector("crm").execute("automatic_ad", {"product": "coffee machine"})
    assert ad["ok"] is True and ad["style"] == "vibrant"


def test_hr_generates_briefs():
    brief = _connector("human_resources").execute("onboarding_video", {"name": "Ana"})
    assert brief["ok"] is True and brief["domain"] == "human_resources"


def test_finance_computes_margin():
    result = _connector("finance").execute("financial_report", {"period": "Q3", "revenue": 1000, "ebitda": 200})
    assert result["ok"] is True
    assert result["meta"]["margin"] == 0.2


def test_bi_kpi_sparkline():
    result = _connector("business_intelligence").execute("visualize_kpi", {"name": "revenue"})
    assert result["ok"] is True
    assert len(result["meta"]["sparkline"]) >= 2
    assert "growth" in result["meta"]


# ── Security bridges ─────────────────────────────────────────────
def test_security_connector_bridges():
    connector = _connector("security")
    assert connector.execute("check_permission", {"role": "admin", "capability": "export"})["granted"] is True
    assert connector.execute("check_permission", {"role": "viewer", "capability": "export"})["granted"] is False
    connector.execute("audit", {"actor": "user1", "action": "export", "target": "video.mp4"})
    encrypted = connector.execute("encrypt", {"plaintext": "secret-value"})
    assert encrypted["encrypted"]
    decrypted = connector.execute("decrypt", {"token": encrypted["encrypted"], "cipher": encrypted["cipher"]})
    assert decrypted["decrypted"] == "secret-value"


# ── Notifications (local outbox) ─────────────────────────────────
def test_notifications_outbox():
    connector = _connector("notifications")
    sent = connector.execute("send_email", {"recipient": "a@b.com", "subject": "Hi", "body": "Hello"})
    assert sent["ok"] is True and sent["channel"] == "email"
    assert connector.execute("send_email", {"recipient": "a@b.com"})["ok"] is False  # missing body
    outbox = connector.execute("outbox")
    assert outbox["email"]["queued"] >= 1


# ── Monitoring / Supervisor ──────────────────────────────────────
def test_monitoring_collectors():
    connector = _connector("monitoring")
    connector.execute("record", {"name": "renders", "seconds": 0.5})
    metrics = connector.execute("metrics")
    assert metrics["counters"]["renders"] == 1
    assert connector.execute("storage")["files"] >= 0
    assert connector.execute("resources")["pid"] > 0


def test_supervisor_ops():
    connector = _connector("supervisor")
    assert connector.execute("remediate", {"issue": "disk_full"})["automatic"] is True
    forecast = connector.execute("forecast", {"series": [10, 12, 14], "horizon": 2})
    assert len(forecast["forecast"]) == 2
    anomalies = connector.execute("detect_anomalies", {"series": [1, 1, 1, 1, 1, 50]})
    assert anomalies["count"] == 1
    plan = connector.execute("distribute", {"jobs": ["a", "b", "c"], "workers": ["w1", "w2"]})
    assert plan["per_worker"]["w1"] == 2


# ── Message bus / Automation / Gateway ───────────────────────────
def test_message_bus_bridges():
    connector = _connector("message_bus")
    connector.execute("kafka_produce", {"topic": "jobs", "message": {"id": 1}})
    consumed = connector.execute("kafka_produce", {"topic": "jobs", "message": {"id": 2}})
    assert consumed["ok"] is True
    streams = connector.execute("stream_add", {"stream": "events", "fields": {"type": "render"}})
    assert streams["entry_id"]


def test_automation_workflow_and_schedule():
    connector = _connector("automation")
    workflow = connector.execute("build_workflow", {"name": "nightly", "steps": ["render", "export"]})
    assert workflow["step_count"] == 2
    assert connector.execute("next_run", {"cron": "0 6 * * *"})["next_run"]


def test_gateway_registers_routes():
    connector = _connector("gateway")
    connector.execute("register_route", {"method": "GET", "path": "/videos"})
    status = connector.execute("status")
    assert status["rest"]["count"] >= 1


# ── Knowledge (RAG) ──────────────────────────────────────────────
def test_knowledge_rag_retrieves():
    connector = _connector("knowledge")
    connector.execute("index_document", {"text": "The studio exports MP4 with H.264."})
    context = connector.execute("rag_context", {"question": "What does the studio export?"})
    assert context["retrieved"] >= 1
    assert "MP4" in context["context"]


# ── Cloud / Learning ─────────────────────────────────────────────
def test_cloud_capabilities():
    connector = _connector("cloud")
    caps = connector.execute("capabilities")
    assert len(caps["providers"]) == 5
    upload = connector.execute("upload_media", {"provider": "aws", "args": {"bucket": "b", "key": "k"}})
    assert upload["ok"] is True and upload["dry_run"] is True


def test_learning_feedback_loop():
    connector = _connector("learning")
    connector.execute("submit_quality", {"output_type": "video", "score": 4.5})
    choice = connector.execute("choose_option", {"options": ["A", "B"]})
    assert choice["choice"] in ("A", "B")
    connector.execute("reward_option", {"option": choice["choice"], "value": 1.0})
    summary = connector.execute("learning_summary")
    assert summary["quality"]["video"]["n"] == 1


# ── Integration manager + API ────────────────────────────────────
def test_integration_manager_registers_connectors():
    from modules.ai_video_studio.integration.integration_manager import (
        get_integration_manager,
    )

    manager = get_integration_manager()
    manager.register_connectors()
    connectors = manager.list_connectors()
    assert len(connectors) == 17
    names = {c["name"] for c in connectors}
    assert "connector.erp" in names
    assert "connector.security" in names


def test_api_connectors_endpoint():
    client = TestClient(_create_app())
    resp = client.get("/api/v1/video-studio/integration/connectors")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 17
    assert data["connectors"]["agriculture"]["domain"] == "agriculture"


def _create_app():
    from modules.ai_video_studio.api.main import create_app

    return create_app()
