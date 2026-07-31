from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class EmailConnector(ProviderConnector):
    """Connector for email sending via SMTP providers (offline simulation)."""

    connector_type = "email"
    display_name = "Email (SMTP)"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self._sent: list[dict[str, Any]] = []
        self.register_many(
            {
                "send": lambda params: self._send(params),
                "list_sent": lambda params: {"messages": list(self._sent), "count": len(self._sent)},
                "get_message": lambda params: self._find(params.get("id", "")),
                "verify_address": lambda params: {"email": params.get("email", ""), "valid": True},
            }
        )

    def _send(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(
            {"kind": "message", "to": params.get("to", ""), "subject": params.get("subject", ""),
             "status": "sent"}
        )
        self._sent.append(record)
        return {"message_id": record["id"], "status": "sent"}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("host") and config.config.get("from"))
