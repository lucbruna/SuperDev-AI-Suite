from __future__ import annotations

import time
from typing import Any

from ..api_logger import APILogger
from .webhook_dispatcher import WebhookDispatcher
from .webhook_models import Webhook, WebhookEvent, WebhookStatus
from .webhook_security import WebhookSecurity
from .webhook_store import WebhookStore


class WebhookManager:
    """Manages webhook registration, lifecycle, and event matching."""

    def __init__(
        self,
        dispatcher: WebhookDispatcher,
        security: WebhookSecurity,
        store: WebhookStore,
        logger: APILogger | None = None,
    ) -> None:
        self._dispatcher = dispatcher
        self._security = security
        self._store = store
        self._logger = logger or APILogger(__name__)

    def register(
        self,
        url: str,
        events: list[str] | None = None,
        *,
        secret: str | None = None,
        retry_count: int = 3,
        timeout: float = 10.0,
        headers: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Webhook:
        wh = Webhook(
            url=url,
            events=events or [WebhookEvent.ALL],
            secret=secret or self._security.generate_secret(),
            retry_count=retry_count,
            timeout=timeout,
            headers=headers or {},
            metadata=metadata or {},
        )
        self._store.save(wh)
        self._logger.info(f"Registered webhook {wh.id} → {wh.url}")
        return wh

    def unregister(self, webhook_id: str) -> bool:
        wh = self._store.get(webhook_id)
        if wh:
            wh.status = WebhookStatus.DISABLED
            self._store.save(wh)
            self._logger.info(f"Disabled webhook {webhook_id}")
            return True
        return False

    def pause(self, webhook_id: str) -> bool:
        wh = self._store.get(webhook_id)
        if wh:
            wh.status = WebhookStatus.PAUSED
            wh.updated_at = time.time()
            self._store.save(wh)
            return True
        return False

    def resume(self, webhook_id: str) -> bool:
        wh = self._store.get(webhook_id)
        if wh and wh.status == WebhookStatus.PAUSED:
            wh.status = WebhookStatus.ACTIVE
            wh.updated_at = time.time()
            self._store.save(wh)
            return True
        return False

    def get_webhook(self, webhook_id: str) -> Webhook | None:
        return self._store.get(webhook_id)

    def list_webhooks(self, status: WebhookStatus | None = None) -> list[Webhook]:
        if status:
            return [wh for wh in self._store.list_all() if wh.status == status]
        return self._store.list_all()

    async def dispatch_event(self, event_type: str, payload: dict[str, Any]) -> int:
        matched = 0
        for wh in self._store.list_all():
            if wh.status != WebhookStatus.ACTIVE:
                continue
            if WebhookEvent.ALL in wh.events or event_type in wh.events:
                await self._dispatcher.dispatch(wh, event_type, payload)
                matched += 1
        self._logger.debug(f"Dispatched '{event_type}' to {matched} webhooks")
        return matched
