"""Tests for the integration subsystem (Fase 11)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.integration import (ApiBridge, EventRouter,
                                              IntegrationEngine, RestClient,
                                              WebhookDispatcher)
from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEventType


class TestEventRouter:
    def test_route_dispatches(self):
        router = EventRouter()
        seen = []
        router.on(EnterpriseKnowledgeEventType.NODE_CREATED,
                  lambda payload: seen.append(payload))
        results = router.route(EnterpriseKnowledgeEventType.NODE_CREATED,
                               {"node_id": "n1"})
        assert len(seen) == 1
        assert results[0]["ok"] is True

    def test_route_no_handler(self):
        router = EventRouter()
        assert router.route(EnterpriseKnowledgeEventType.NODE_CREATED,
                            {"node_id": "n1"}) == []

    def test_handler_exception_isolated(self):
        router = EventRouter()

        def boom(_payload):
            raise ValueError("boom")

        router.on(EnterpriseKnowledgeEventType.SEARCH_EXECUTED, boom)
        results = router.route(EnterpriseKnowledgeEventType.SEARCH_EXECUTED, {})
        assert results[0]["ok"] is False
        assert "boom" in results[0]["error"]

    def test_off_and_counts(self):
        router = EventRouter()
        handler = lambda _payload: None  # noqa: E731
        router.on(EnterpriseKnowledgeEventType.MEMORY_STORED, handler)
        router.off(EnterpriseKnowledgeEventType.MEMORY_STORED, handler)
        assert router.counts() == {}


class TestRestClient:
    def test_get_connection_error(self):
        client = RestClient(timeout=1.0)
        result = client.get("http://127.0.0.1:1/health")
        assert result["ok"] is False
        assert result["status"] == 0

    def test_headers_merge(self):
        client = RestClient(headers={"Authorization": "Bearer x"})
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["Authorization"] == "Bearer x"


class TestWebhookDispatcher:
    def test_register_and_list(self):
        dispatcher = WebhookDispatcher()
        dispatcher.register("slack", "https://hooks.slack.com/1")
        dispatcher.register("slack", "https://hooks.slack.com/2")
        assert dispatcher.webhooks()["slack"] == [
            "https://hooks.slack.com/1", "https://hooks.slack.com/2"]

    def test_unregister(self):
        dispatcher = WebhookDispatcher()
        dispatcher.register("slack", "https://hooks.slack.com/1")
        assert dispatcher.unregister("slack",
                                     "https://hooks.slack.com/1") is True
        assert dispatcher.unregister("slack",
                                     "https://hooks.slack.com/1") is False

    def test_dispatch_failure_tracked(self):
        dispatcher = WebhookDispatcher(RestClient(timeout=1.0))
        dispatcher.register("slack", "http://127.0.0.1:1/hook")
        results = dispatcher.dispatch(EnterpriseKnowledgeEventType.MEMORY_STORED,
                                      {"memory_id": "m1"})
        assert results[0]["ok"] is False
        assert dispatcher.stats()["failed"] == 1


class TestApiBridge:
    def test_register_and_handle(self):
        bridge = ApiBridge()
        bridge.register("echo", lambda text: {"text": text})
        result = bridge.handle("echo", {"text": "oi"})
        assert result["ok"] is True
        assert result["data"] == {"text": "oi"}

    def test_unknown_operation(self):
        bridge = ApiBridge()
        result = bridge.handle("nope")
        assert result["ok"] is False
        assert result["error"] == "unknown_operation"

    def test_invalid_params(self):
        bridge = ApiBridge()
        bridge.register("echo", lambda text: {"text": text})
        result = bridge.handle("echo", {})
        assert result["ok"] is False
        assert result["error"] == "invalid_params"

    def test_operation_error_surfaced(self):
        bridge = ApiBridge()

        def broken(_text):
            raise RuntimeError("crash")

        bridge.register("broken", broken)
        result = bridge.handle("broken", {"_text": "x"})
        assert result["ok"] is False
        assert result["error"] == "internal"


class TestIntegrationEngine:
    def test_bridge_flow(self):
        engine = IntegrationEngine()
        engine.register_operation("ping", lambda: "pong")
        result = engine.handle_api("ping")
        assert result["data"] == "pong"
        assert engine.operations() == ["ping"]

    def test_event_route_and_webhook(self):
        engine = IntegrationEngine()
        engine.register_webhook("slack", "http://127.0.0.1:1/hook")
        results = engine.dispatch_event(
            EnterpriseKnowledgeEventType.MEMORY_STORED,
            {"memory_id": "m1"})
        assert len(results) == 1
        assert results[0]["ok"] is False

    def test_stats(self):
        engine = IntegrationEngine()
        engine.register_operation("ping", lambda: "pong")
        engine.register_webhook("slack", "http://127.0.0.1:1/hook")
        stats = engine.stats()
        assert stats["bridge"]["operations"] == 1
        assert stats["webhooks"]["registered"] == 1
