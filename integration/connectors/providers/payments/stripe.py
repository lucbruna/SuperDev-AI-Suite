from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class StripeConnector(ProviderConnector):
    """Connector for Stripe payments (offline in-memory simulation)."""

    connector_type = "stripe"
    display_name = "Stripe"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "create_payment_intent": lambda params: self._create_intent(params),
                "confirm_payment_intent": lambda params: self._update(params.get("id", ""), {"status": "succeeded"}),
                "list_payment_intents": lambda params: self._query(params),
                "create_customer": lambda params: self._add({"kind": "customer", **params.get("customer", {})}),
                "list_customers": lambda params: {"customers": self._all({"kind": "customer"})},
                "create_refund": lambda params: self._update(params.get("payment_intent", ""), {"status": "refunded"}),
            }
        )

    def _create_intent(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(
            {"kind": "payment_intent", "amount": params.get("amount", 0),
             "currency": params.get("currency", "brl"), "status": "requires_confirmation"}
        )
        return {"id": record["id"], "client_secret": f"pi_{record['id']}_secret", "status": "requires_confirmation"}

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        rows = self._all({"kind": "payment_intent"})
        return {"data": rows, "has_more": False}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("secret_key"))
