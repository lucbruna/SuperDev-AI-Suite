"""Connectors registry — aggregates every Volume 10 domain connector.

Lazy imports keep package import cycle-free: importing this module never
pulls the connector implementations until ``get_connectors`` is called.
"""
from __future__ import annotations

from typing import Any

#: (domain, module path, connector accessor name)
_CONNECTOR_SPECS: tuple[tuple[str, str, str], ...] = (
    ("enterprise_ai", "enterprise_ai.enterprise_ai_connector", "get_enterprise_ai_connector"),
    ("agriculture", "agriculture_ai.agriculture_connector", "get_agriculture_connector"),
    ("erp", "erp.erp_connector", "get_erp_connector"),
    ("crm", "crm.crm_connector", "get_crm_connector"),
    ("human_resources", "human_resources.hr_connector", "get_hr_connector"),
    ("finance", "finance.finance_connector", "get_finance_connector"),
    ("business_intelligence", "business_intelligence.bi_connector", "get_bi_connector"),
    ("security", "security.security_connector", "get_security_connector"),
    ("automation", "automation.automation_connector", "get_automation_connector"),
    ("notifications", "notifications.notification_connector", "get_notification_connector"),
    ("knowledge", "knowledge.knowledge_connector", "get_knowledge_connector"),
    ("cloud", "cloud.cloud_connector", "get_cloud_connector"),
    ("monitoring", "monitoring.monitoring_connector", "get_monitoring_connector"),
    ("supervisor", "supervisor.supervisor_connector", "get_supervisor_connector"),
    ("gateway", "gateway.api_gateway", "get_api_gateway"),
    ("message_bus", "message_bus.message_bus_connector", "get_message_bus_connector"),
    ("learning", "learning.enterprise_learning", "get_enterprise_learning_connector"),
)

_connectors: dict[str, Any] | None = None


def get_connectors() -> dict[str, Any]:
    """All domain connectors, keyed by domain (lazy, cached)."""
    global _connectors
    if _connectors is None:
        connectors: dict[str, Any] = {}
        for domain, module_path, accessor in _CONNECTOR_SPECS:
            try:
                module = __import__(
                    f"{__name__.rsplit('.', 1)[0]}.{module_path}", fromlist=[accessor]
                )
                connectors[domain] = getattr(module, accessor)()
            except Exception:  # noqa: BLE001 — a broken connector must not break the registry
                connectors[domain] = None
        _connectors = connectors
    return _connectors


def connector_domains() -> list[str]:
    return [domain for domain, _, _ in _CONNECTOR_SPECS]


def connector_count() -> int:
    return len(_CONNECTOR_SPECS)
