"""Webhook dispatch for knowledge events."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.integration.rest_client import RestClient
from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEventType
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics


class WebhookDispatcher:
    """Forwards event payloads to registered webhook URLs."""

    def __init__(self, client: RestClient | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None) -> None:
        self.client = client or RestClient(timeout=3.0)
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self._webhooks: dict[str, list[str]] = {}

    def register(self, name: str, url: str) -> None:
        self._webhooks.setdefault(name, []).append(url)

    def unregister(self, name: str, url: str | None = None) -> bool:
        if name not in self._webhooks:
            return False
        if url is None:
            del self._webhooks[name]
            return True
        urls = self._webhooks[name]
        if url in urls:
            urls.remove(url)
            return True
        return False

    def webhooks(self) -> dict[str, list[str]]:
        return {name: list(urls) for name, urls in self._webhooks.items()}

    def dispatch(self, event_type: EnterpriseKnowledgeEventType,
                 payload: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for name, urls in self._webhooks.items():
            for url in urls:
                response = self.client.post(url, {
                    "event": event_type.value, "payload": payload})
                ok = bool(response.get("ok"))
                results.append({"webhook": name, "url": url, "ok": ok,
                                "status": response.get("status")})
                self.metrics.increment(
                    "ek.webhook_delivered" if ok else "ek.webhook_failed")
        return results

    def stats(self) -> dict[str, Any]:
        counters = self.metrics.snapshot()["counters"]
        return {
            "registered": sum(len(urls)
                              for urls in self._webhooks.values()),
            "delivered": counters.get("ek.webhook_delivered", 0),
            "failed": counters.get("ek.webhook_failed", 0),
        }
