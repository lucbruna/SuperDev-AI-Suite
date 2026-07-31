from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class SMSConnector(ProviderConnector):
    """Connector for SMS sending (offline in-memory simulation)."""

    connector_type = "sms"
    display_name = "SMS"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self._sent: list[dict[str, Any]] = []
        self.register_many(
            {
                "send": lambda params: self._send(params),
                "list_sent": lambda params: {"messages": list(self._sent), "count": len(self._sent)},
                "get_status": lambda params: {"message_id": params.get("id", ""), "status": "delivered"},
                "balance": lambda params: {"balance": 42.5, "currency": "BRL"},
            }
        )

    def _send(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(
            {"kind": "sms", "to": params.get("to", ""), "body": params.get("body", ""), "status": "sent"}
        )
        self._sent.append(record)
        return {"message_id": record["id"], "status": "sent"}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("api_key"))
