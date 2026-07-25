from __future__ import annotations

import asyncio
import sys
from typing import Any

from workflow_engine.nodes.base_node import BaseNode, NodeResult
from workflow_engine.graph.node import NodeType


class ShellNode(BaseNode):
    node_type: NodeType = NodeType.SHELL

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        command = self.config.get("command", "")
        timeout = self.config.get("timeout", 60)

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            return NodeResult(
                node_id=self.config.get("node_id", ""),
                status="failed",
                error=f"Shell command timed out after {timeout}s",
            )
        except Exception as e:
            return NodeResult(
                node_id=self.config.get("node_id", ""),
                status="failed",
                error=f"Shell command failed: {e}",
            )

        return_code = proc.returncode or 0
        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success" if return_code == 0 else "failed",
            output={
                "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                "return_code": return_code,
            },
            error=None if return_code == 0 else stderr.decode("utf-8", errors="replace") if stderr else f"Exit code {return_code}",
        )
