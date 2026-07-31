from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class EcommerceConnector(ProviderConnector):
    """Connector for e-commerce platforms (offline in-memory simulation)."""

    connector_type = "ecommerce"
    display_name = "E-commerce"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_products": lambda params: self._query(params, "product"),
                "create_product": lambda params: self._insert(params, "product"),
                "update_product_stock": lambda params: self._update(params.get("id", ""), {"stock": params.get("stock", 0)}),
                "list_orders": lambda params: self._query(params, "order"),
                "get_order": lambda params: self._find(params.get("id", "")),
                "update_order_status": lambda params: self._update(params.get("id", ""), {"status": params.get("status", "")}),
                "list_customers": lambda params: self._query(params, "customer"),
                "list_carts": lambda params: self._query(params, "cart"),
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
        return bool(config.config.get("store_url") and config.config.get("access_token"))
