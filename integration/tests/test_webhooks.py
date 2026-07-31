"""Tests for the webhooks subsystem (webhooks/)."""

from __future__ import annotations

from typing import Any

from integration.webhooks.history import WebhookHistory
from integration.webhooks.receiver import WebhookReceiver
from integration.webhooks.retry import RetryManager, RetryPolicy
from integration.webhooks.sender import WebhookSender
from integration.webhooks.signature import WebhookSignature
from integration.webhooks.validator import WebhookValidator
from integration.webhooks.webhook_engine import WebhookEngine


class TestWebhookSignature:
    def test_sign_and_verify(self) -> None:
        sig = WebhookSignature("secret")
        payload = {"order_id": "123", "amount": 99.9}
        signature = sig.sign(payload)
        assert signature.startswith("sha256=")
        assert sig.verify(payload, signature) is True
        assert sig.verify({"order_id": "999"}, signature) is False

    def test_consistent_digest(self) -> None:
        sig = WebhookSignature("s")
        assert sig.sign({"a": 1}) == sig.sign({"a": 1})
        assert sig.sign({"a": 1}) != sig.sign({"a": 2})


class TestWebhookValidator:
    def test_schema_validation(self) -> None:
        validator = WebhookValidator()
        validator.register_schema("order.created", {
            "order_id": "str",
            "amount": "float",
        })
        assert validator.is_valid("order.created",
                                  {"order_id": "1", "amount": 10.0}) is True
        errors = validator.validate("order.created", {"order_id": "1"})
        assert any("amount" in e for e in errors)
        errors = validator.validate("order.created",
                                    {"order_id": "1", "amount": "not-a-number"})
        assert any("expected 'float'" in e for e in errors)

    def test_unregistered_passes(self) -> None:
        validator = WebhookValidator()
        assert validator.is_valid("anything", {"x": 1}) is True


class TestWebhookHistory:
    def test_record_and_count(self) -> None:
        history = WebhookHistory()
        history.record("e1", "accepted", 1)
        history.record("e2", "rejected", 1, "bad signature")
        assert history.count() == 2
        assert history.count("accepted") == 1
        assert history.count("rejected") == 1
        assert history.list()[0]["event_id"] == "e1"

    def test_clear(self) -> None:
        history = WebhookHistory()
        history.record("e1", "delivered", 1)
        history.clear()
        assert history.count() == 0


class TestRetry:
    def test_policy(self) -> None:
        policy = RetryPolicy(max_attempts=3, backoff=1.0, factor=2.0)
        assert policy.should_retry(1) is True
        assert policy.should_retry(3) is True
        assert policy.should_retry(4) is False
        assert policy.next_delay(1) == 1.0
        assert policy.next_delay(2) == 2.0
        assert policy.next_delay(3) == 4.0

    def test_manager_tracks_attempts(self) -> None:
        manager = RetryManager(RetryPolicy(max_attempts=2))
        assert manager.register("evt") == 1
        assert manager.register("evt") == 2
        assert manager.attempts("evt") == 2
        assert manager.should_retry("evt") is False
        manager.clear("evt")
        assert manager.attempts("evt") == 0


class TestWebhookReceiver:
    def test_handle_with_signature(self) -> None:
        receiver = WebhookReceiver(secret="s")
        calls: list[dict[str, Any]] = []
        receiver.on("order.created", lambda p: calls.append(p))
        sig = WebhookSignature("s").sign({"order_id": "1"})
        assert receiver.handle("order.created", {"order_id": "1"}, sig) is True
        assert len(calls) == 1
        assert receiver.count() == 1

    def test_reject_bad_signature(self) -> None:
        receiver = WebhookReceiver(secret="s")
        receiver.on("order.created", lambda p: None)
        bad = WebhookSignature("other").sign({"order_id": "1"})
        assert receiver.handle("order.created", {"order_id": "1"}, bad) is False
        assert receiver.count() == 0


class TestWebhookSender:
    def test_send_receipt(self) -> None:
        sender = WebhookSender(secret="s")
        receipt = sender.send("https://example.com/hook", "order.created",
                              {"order_id": "1"})
        assert receipt["delivered"] is True
        assert receipt["url"] == "https://example.com/hook"
        assert receipt["signature"].startswith("sha256=")
        assert sender.count() == 1
        assert sender.deliveries(1)[0]["event_id"] == receipt["event_id"]


class TestWebhookEngine:
    def test_dispatch_and_notify(self) -> None:
        engine = WebhookEngine(secret="s")
        engine.register("order.created", {
            "order_id": "str",
            "amount": "float",
        })
        sig = WebhookSignature("s").sign({"order_id": "1", "amount": 10.0})
        assert engine.dispatch("order.created",
                               {"order_id": "1", "amount": 10.0}, sig) is True
        assert engine.dispatch("order.created",
                               {"order_id": "1", "amount": "x"}, sig) is False
        receipt = engine.notify("https://example.com/hook",
                                "order.created", {"order_id": "2", "amount": 5.0})
        assert receipt["delivered"] is True

    def test_stats(self) -> None:
        engine = WebhookEngine(secret="s")
        sig = WebhookSignature("s").sign({"x": 1})
        engine.dispatch("evt", {"x": 1}, sig)
        engine.notify("https://example.com", "evt", {"x": 1})
        stats = engine.stats()
        assert stats["accepted"] == 1
        assert stats["delivered"] == 1
        assert stats["sent"] == 1
        assert stats["received"] == 1
