from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class AzureConnector(ProviderConnector):
    """Connector for Microsoft Azure cloud services (offline simulation)."""

    connector_type = "azure"
    display_name = "Microsoft Azure"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_services": lambda params: {
                    "services": ["blob", "vm", "functions", "sql", "event-hubs"]
                },
                "list_vms": lambda params: self._query(params),
                "create_vm": lambda params: self._insert(params),
                "deallocate_vm": lambda params: self._update(params.get("id", ""), {"state": "deallocated"}),
                "list_blobs": lambda params: {"blobs": [r for r in self._records if r.get("kind") == "blob"]},
                "invoke_function": lambda params: {"result": f"function {params.get('name', '')} executed", "ok": True},
            }
        )

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        rows = self._all(params.get("filters"))
        return {"vms": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add({"kind": "vm", **params.get("vm", {})})
        return {"vm_id": record["id"], "state": "running"}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("tenant_id") and config.config.get("subscription_id"))
