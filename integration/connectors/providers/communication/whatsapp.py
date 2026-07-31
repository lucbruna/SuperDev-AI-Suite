from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class WhatsAppConnector(ProviderConnector):
    """Connector for WhatsApp Business messages (offline simulation)."""

    connector_type = "whatsapp"
    display_name = "WhatsApp Business"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self._sent: list[dict[str, Any]] = []
        self.register_many(
            {
                "send_text": lambda params: self._send(params, "text"),
                "send_template": lambda params: self._send(params, "template"),
                "list_sent": lambda params: {"messages": list(self._sent), "count": len(self._sent)},
                "get_status": lambda params: {"phone": params.get("phone", ""), "status": "delivered"},
                "list_templates": lambda params: {"templates": ["welcome", "order_update", "payment_reminder"]},
            }
        )

    def _send(self, params: dict[str, Any], kind: str) -> dict[str, Any]:
        self._require_connected()
        record = self._add(
            {"kind": "wa_message", "to": params.get("to", ""), "type": kind, "status": "queued"}
        )
        self._sent.append(record)
        return {"message_id": record["id"], "status": "queued", "wamid": f"wamid.{record['id']}"}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("token") and config.config.get("phone_number_id"))
