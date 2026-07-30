from __future__ import annotations

import json
import os
from typing import Any

from ..api_logger import APILogger
from .webhook_models import Webhook


class WebhookStore:
    """In-memory webhook persistence with optional JSON file backup."""

    def __init__(self, file_path: str | None = None, logger: APILogger | None = None) -> None:
        self._webhooks: dict[str, Webhook] = {}
        self._file_path = file_path
        self._logger = logger or APILogger(__name__)

        if file_path and os.path.exists(file_path):
            self._load()

    def save(self, webhook: Webhook) -> None:
        self._webhooks[webhook.id] = webhook
        if self._file_path:
            self._persist()

    def get(self, webhook_id: str) -> Webhook | None:
        return self._webhooks.get(webhook_id)

    def delete(self, webhook_id: str) -> bool:
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            if self._file_path:
                self._persist()
            return True
        return False

    def list_all(self) -> list[Webhook]:
        return list(self._webhooks.values())

    def count(self) -> int:
        return len(self._webhooks)

    def clear(self) -> None:
        self._webhooks.clear()
        if self._file_path and os.path.exists(self._file_path):
            os.remove(self._file_path)

    def _persist(self) -> None:
        if not self._file_path:
            return
        data: list[dict[str, Any]] = []
        for wh in self._webhooks.values():
            d = {
                "id": wh.id,
                "url": wh.url,
                "events": wh.events,
                "secret": wh.secret,
                "status": wh.status.value,
                "retry_count": wh.retry_count,
                "timeout": wh.timeout,
                "headers": wh.headers,
                "created_at": wh.created_at,
                "updated_at": wh.updated_at,
                "last_delivery": wh.last_delivery,
                "metadata": wh.metadata,
            }
            data.append(d)

        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        with open(self._file_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        if not self._file_path or not os.path.exists(self._file_path):
            return
        try:
            with open(self._file_path) as f:
                data: list[dict[str, Any]] = json.load(f)
            for d in data:
                wh = Webhook(
                    id=d["id"],
                    url=d["url"],
                    events=d["events"],
                    secret=d["secret"],
                    status=d["status"],
                    retry_count=d["retry_count"],
                    timeout=d["timeout"],
                    headers=d["headers"],
                    created_at=d["created_at"],
                    updated_at=d["updated_at"],
                    last_delivery=d.get("last_delivery"),
                    metadata=d.get("metadata", {}),
                )
                self._webhooks[wh.id] = wh
            self._logger.info(f"Loaded {len(data)} webhooks from {self._file_path}")
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            self._logger.error(f"Failed to load webhooks from {self._file_path}: {exc}")
