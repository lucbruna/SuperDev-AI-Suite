from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class GoogleCloudConnector(ProviderConnector):
    """Connector for Google Cloud Platform (offline in-memory simulation)."""

    connector_type = "google"
    display_name = "Google Cloud"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_services": lambda params: {
                    "services": ["gcs", "gce", "cloud-functions", "bigquery", "pubsub"]
                },
                "list_instances": lambda params: self._query(params),
                "create_instance": lambda params: self._insert(params),
                "stop_instance": lambda params: self._update(params.get("id", ""), {"state": "stopped"}),
                "list_buckets": lambda params: {"buckets": [r for r in self._records if r.get("kind") == "bucket"]},
                "query_bigquery": lambda params: {"rows": [], "ok": True},
            }
        )

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        rows = self._all(params.get("filters"))
        return {"instances": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add({"kind": "instance", **params.get("instance", {})})
        return {"instance_id": record["id"], "state": "running"}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("project_id"))
