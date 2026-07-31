from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class PixConnector(ProviderConnector):
    """Connector for Brazilian Pix instant payments (offline simulation)."""

    connector_type = "pix"
    display_name = "Pix (Bacen)"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "create_charge": lambda params: self._create_charge(params),
                "list_charges": lambda params: self._query(params),
                "get_charge": lambda params: self._find(params.get("id", "")),
                "refund": lambda params: self._update(params.get("id", ""), {"status": "refunded"}),
                "list_pix_keys": lambda params: {"keys": ["cpf", "cnpj", "email", "phone", "random"]},
                "webhook_config": lambda params: {"webhook_url": params.get("url", ""), "ok": True},
            }
        )

    def _create_charge(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(
            {"kind": "charge", "amount_cents": params.get("amount_cents", 0),
             "key": params.get("key", ""), "status": "pending", **params.get("metadata", {})}
        )
        return {"charge_id": record["id"], "pix_copiaecola": f"00020126{record['id']}52040000", "status": "pending"}

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        rows = self._all({"kind": "charge"})
        return {"charges": rows, "count": len(rows)}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("client_id") and config.config.get("client_secret"))
