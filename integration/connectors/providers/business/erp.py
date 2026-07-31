from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class ERPConnector(ProviderConnector):
    """Connector for ERP systems (offline in-memory simulation).

    Used for the "connect ERP to financial system" scenario: exposes order,
    invoice, product, and fiscal operations.
    """

    connector_type = "erp"
    display_name = "ERP"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_orders": lambda params: self._query(params, "order"),
                "get_order": lambda params: self._find(params.get("id", "")),
                "create_order": lambda params: self._insert(params, "order"),
                "update_order_status": lambda params: self._update(params.get("id", ""), {"status": params.get("status", "")}),
                "list_invoices": lambda params: self._query(params, "invoice"),
                "create_invoice": lambda params: self._insert(params, "invoice"),
                "list_products": lambda params: self._query(params, "product"),
                "list_fiscal_documents": lambda params: self._query(params, "fiscal"),
                "list_customers": lambda params: self._query(params, "customer"),
                "sync_financial": lambda params: {"synced": True, "source": "erp", "target": "financial"},
            }
        )

    def _query(self, params: dict[str, Any], kind: str) -> dict[str, Any]:
        self._require_connected()
        rows = self._all({"kind": kind})
        return {f"{kind}s": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any], kind: str) -> dict[str, Any]:
        self._require_connected()
        record = self._add({"kind": kind, **params.get("record", {})})
        return {"id": record["id"], "record": record}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("base_url") and config.config.get("api_key"))
