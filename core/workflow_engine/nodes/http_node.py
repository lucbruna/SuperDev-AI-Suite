from __future__ import annotations

from typing import Any

import httpx

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult


class HTTPNode(BaseNode):
    node_type: NodeType = NodeType.HTTP

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        url = self.config.get("url", "")
        method = self.config.get("method", "GET").upper()
        headers = self.config.get("headers", {})
        body = self.config.get("body")
        timeout = self.config.get("timeout", 30)

        resolved_url = url
        if isinstance(url, str) and "{context" in url:
            resolved_url = url.format(context=context)

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
                response = await client.request(method, resolved_url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json() if response.status_code != 204 else None
        except Exception as e:
            return NodeResult(
                node_id=self.config.get("node_id", ""),
                status="failed",
                error=f"HTTP request failed: {e}",
            )

        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success",
            output={
                "status_code": response.status_code,
                "data": data,
                "headers": dict(response.headers),
            },
        )
