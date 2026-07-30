from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.webhooks import WebhookManager, WebhookDispatcher, WebhookSecurity, WebhookStore  # noqa: E402
from api.webhooks.webhook_manager import Webhook, WebhookStatus, WebhookEvent  # noqa: E402


class TestWebhookSecurity:
    def test_generate_secret(self) -> None:
        security = WebhookSecurity()
        secret = security.generate_secret()
        assert len(secret) == 64  # 32 bytes hex

    def test_sign_and_verify(self) -> None:
        security = WebhookSecurity()
        secret = security.generate_secret()
        payload = b'{"event": "test"}'
        signature = security.sign(payload, secret)
        assert security.verify(payload, secret, signature)

    def test_verify_wrong_secret(self) -> None:
        security = WebhookSecurity()
        payload = b'{"event": "test"}'
        signature = security.sign(payload, "secret1")
        assert not security.verify(payload, "secret2", signature)

    def test_verify_request(self) -> None:
        security = WebhookSecurity()
        secret = security.generate_secret()
        payload = b'{"event": "test"}'
        signature = security.sign(payload, secret)
        valid, msg = security.verify_request(payload, signature, secret)
        assert valid


class TestWebhookStore:
    def test_save_and_get(self) -> None:
        store = WebhookStore()
        wh = Webhook(url="https://example.com/hook", events=["test.event"])
        store.save(wh)
        retrieved = store.get(wh.id)
        assert retrieved is not None
        assert retrieved.url == "https://example.com/hook"

    def test_delete(self) -> None:
        store = WebhookStore()
        wh = Webhook(url="https://example.com/hook")
        store.save(wh)
        assert store.delete(wh.id)
        assert store.get(wh.id) is None

    def test_list_all(self) -> None:
        store = WebhookStore()
        store.save(Webhook(url="https://a.com"))
        store.save(Webhook(url="https://b.com"))
        assert len(store.list_all()) == 2

    def test_count(self) -> None:
        store = WebhookStore()
        assert store.count() == 0
        store.save(Webhook(url="https://a.com"))
        assert store.count() == 1


class TestWebhookManager:
    def test_register_webhook(self) -> None:
        security = WebhookSecurity()
        dispatcher = WebhookDispatcher(security)
        store = WebhookStore()
        mgr = WebhookManager(dispatcher, security, store)
        wh = mgr.register("https://example.com/hook", ["test.event"])
        assert wh.url == "https://example.com/hook"
        assert wh.status == WebhookStatus.ACTIVE

    def test_pause_resume(self) -> None:
        security = WebhookSecurity()
        dispatcher = WebhookDispatcher(security)
        store = WebhookStore()
        mgr = WebhookManager(dispatcher, security, store)
        wh = mgr.register("https://example.com/hook")
        assert mgr.pause(wh.id)
        assert mgr.get_webhook(wh.id) is not None  # type: ignore[union-attr]
        assert mgr.resume(wh.id)

    def test_list_by_status(self) -> None:
        security = WebhookSecurity()
        dispatcher = WebhookDispatcher(security)
        store = WebhookStore()
        mgr = WebhookManager(dispatcher, security, store)
        mgr.register("https://a.com")
        mgr.register("https://b.com")
        assert len(mgr.list_webhooks()) == 2


class TestWebhookDispatcher:
    def test_initialization(self) -> None:
        security = WebhookSecurity()
        dispatcher = WebhookDispatcher(security)
        assert dispatcher is not None

    def test_delivery_history(self) -> None:
        security = WebhookSecurity()
        dispatcher = WebhookDispatcher(security)
        assert dispatcher.get_delivery_history() == []
