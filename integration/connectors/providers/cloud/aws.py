from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class AWSConnector(ProviderConnector):
    """Connector for AWS cloud services (offline in-memory simulation)."""

    connector_type = "aws"
    display_name = "AWS"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_services": lambda params: {
                    "services": ["s3", "ec2", "lambda", "rds", "sqs"]
                },
                "list_instances": lambda params: self._query(params),
                "launch_instance": lambda params: self._insert(params),
                "stop_instance": lambda params: self._update(params.get("id", ""), {"state": "stopped"}),
                "list_buckets": lambda params: {"buckets": [r for r in self._records if r.get("kind") == "bucket"]},
                "invoke_lambda": lambda params: {"result": f"lambda {params.get('name', '')} executed", "ok": True},
            }
        )

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        filters = params.get("filters")
        rows = self._all(filters)
        return {"instances": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add({"kind": "instance", **params.get("instance", {})})
        return {"instance_id": record["id"], "state": "running"}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("access_key") and config.config.get("region"))
