from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class PaymentGatewayConnector(ProviderConnector):
    """Generic payment gateway connector for cards and bank transfers (offline)."""

    connector_type = "payment_gateway"
    display_name = "Payment Gateway"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "charge_card": lambda params: self._charge_card(params),
                "list_transactions": lambda params: self._query(params),
                "get_transaction": lambda params: self._find(params.get("id", "")),
                "capture": lambda params: self._update(params.get("id", ""), {"status": "captured"}),
                "refund": lambda params: self._update(params.get("id", ""), {"status": "refunded"}),
                "gateway_status": lambda params: {"status": "operational", "latency_ms": 12},
            }
        )

    def _charge_card(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(
            {"kind": "transaction", "amount": params.get("amount", 0),
             "currency": params.get("currency", "brl"),
             "card_brand": params.get("card_brand", "visa"), "status": "authorized"}
        )
        return {"transaction_id": record["id"], "status": "authorized", "brand": params.get("card_brand", "visa")}

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        rows = self._all({"kind": "transaction"})
        return {"transactions": rows, "count": len(rows)}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("merchant_id") and config.config.get("api_key"))
