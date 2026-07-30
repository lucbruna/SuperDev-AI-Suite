from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any

from ..api_logger import APILogger
from .webhook_models import Webhook
from .webhook_security import WebhookSecurity


class WebhookDispatcher:
    """Delivers webhook payloads to registered endpoints."""

    def __init__(self, security: WebhookSecurity, logger: APILogger | None = None) -> None:
        self._security = security
        self._logger = logger or APILogger(__name__)
        self._delivery_history: list[dict[str, Any]] = []
        self._max_history = 1000

    async def dispatch(self, webhook: Webhook, event_type: str, payload: dict[str, Any]) -> bool:
        body = {
            "event": event_type,
            "timestamp": time.time(),
            "webhook_id": webhook.id,
            "data": payload,
        }
        body_bytes = json.dumps(body).encode("utf-8")
        signature = self._security.sign(body_bytes, webhook.secret)

        req = urllib.request.Request(
            webhook.url,
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Event": event_type,
                "X-Webhook-ID": webhook.id,
                **webhook.headers,
            },
            method="POST",
        )

        for attempt in range(webhook.retry_count):
            start = time.monotonic()
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: urllib.request.urlopen(req, timeout=int(webhook.timeout)),
                )
                elapsed = time.monotonic() - start
                status_code = result.getcode()
                self._record_delivery(webhook.id, event_type, status_code, elapsed, attempt)
                self._logger.info(f"Webhook {webhook.id} delivered ({status_code}) in {elapsed:.2f}s")
                return True

            except urllib.error.HTTPError as exc:
                elapsed = time.monotonic() - start
                status_code = exc.code
                self._record_delivery(webhook.id, event_type, status_code, elapsed, attempt, str(exc))
                if attempt < webhook.retry_count - 1 and status_code >= 500:
                    wait = 2.0 ** attempt
                    self._logger.warning(f"Webhook {webhook.id} HTTP {status_code}, retry in {wait:.0f}s")
                    await asyncio.sleep(wait)
                else:
                    self._logger.error(f"Webhook {webhook.id} failed HTTP {status_code}: {exc}")
                    return False

            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                elapsed = time.monotonic() - start
                self._record_delivery(webhook.id, event_type, 0, elapsed, attempt, str(exc))
                if attempt < webhook.retry_count - 1:
                    wait = 2.0 ** attempt
                    self._logger.warning(f"Webhook {webhook.id} error, retry in {wait:.0f}s")
                    await asyncio.sleep(wait)
                else:
                    self._logger.error(f"Webhook {webhook.id} exhausted retries: {exc}")
                    return False

        return False

    def _record_delivery(
        self,
        webhook_id: str,
        event_type: str,
        status_code: int,
        elapsed: float,
        attempt: int,
        error: str | None = None,
    ) -> None:
        record: dict[str, Any] = {
            "webhook_id": webhook_id,
            "event_type": event_type,
            "status_code": status_code,
            "elapsed": elapsed,
            "attempt": attempt,
            "timestamp": time.time(),
        }
        if error:
            record["error"] = error
        self._delivery_history.append(record)
        if len(self._delivery_history) > self._max_history:
            self._delivery_history.pop(0)

    def get_delivery_history(self, webhook_id: str | None = None) -> list[dict[str, Any]]:
        if webhook_id:
            return [r for r in self._delivery_history if r["webhook_id"] == webhook_id]
        return list(self._delivery_history)

    def clear_history(self) -> None:
        self._delivery_history.clear()
