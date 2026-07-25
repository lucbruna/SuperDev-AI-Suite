from __future__ import annotations

import io
import sys
import traceback
from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult


class PythonNode(BaseNode):
    node_type: NodeType = NodeType.PYTHON

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        code = self.config.get("code", "")
        imports = self.config.get("imports", [])

        exec_globals: dict[str, Any] = {"context": context, "__builtins__": __builtins__}
        for import_stmt in imports:
            try:
                exec(import_stmt, exec_globals)
            except Exception as e:
                return NodeResult(
                    node_id=self.config.get("node_id", ""),
                    status="failed",
                    error=f"Import error: {e}",
                )

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exec(code, exec_globals)
            output = exec_globals.get("result", sys.stdout.getvalue())
        except Exception:
            return NodeResult(
                node_id=self.config.get("node_id", ""),
                status="failed",
                error=traceback.format_exc(),
            )
        finally:
            sys.stdout = old_stdout

        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success",
            output={"result": output, "stdout": sys.stdout.getvalue() if hasattr(sys.stdout, "getvalue") else ""},
        )
