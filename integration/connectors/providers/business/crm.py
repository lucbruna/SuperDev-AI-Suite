from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class CRMConnector(ProviderConnector):
    """Connector for CRM systems (offline in-memory simulation)."""

    connector_type = "crm"
    display_name = "CRM"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_leads": lambda params: self._query(params, "lead"),
                "create_lead": lambda params: self._insert(params, "lead"),
                "update_lead_status": lambda params: self._update(params.get("id", ""), {"status": params.get("status", "")}),
                "list_contacts": lambda params: self._query(params, "contact"),
                "create_contact": lambda params: self._insert(params, "contact"),
                "list_opportunities": lambda params: self._query(params, "opportunity"),
                "create_opportunity": lambda params: self._insert(params, "opportunity"),
                "list_deals": lambda params: self._query(params, "deal"),
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
        return bool(config.config.get("base_url") and config.config.get("token"))
