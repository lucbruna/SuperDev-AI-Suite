from __future__ import annotations

import io
import sys
import traceback
from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult

from core.safe_exec import safe_builtins, safe_exec, validate_import_statement


class PythonNode(BaseNode):
    node_type: NodeType = NodeType.PYTHON

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        code = self.config.get("code", "")
        imports = self.config.get("imports", [])

        # Restricted execution namespace — no full builtins (OWASP A03).
        exec_globals: dict[str, Any] = {"context": context,
                                        "__builtins__": safe_builtins()}
        for import_stmt in imports:
            try:
                validate_import_statement(import_stmt)
                exec(compile(import_stmt, "<safe-import>", "exec"),
                     exec_globals)
            except Exception as e:
                return NodeResult(
                    node_id=self.config.get("node_id", ""),
                    status="failed",
                    error=f"Import error: {e}",
                )

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            ns = safe_exec(code, exec_globals)
            output = ns.get("result", sys.stdout.getvalue())
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
            output={"result": output,
                    "stdout": (sys.stdout.getvalue()
                               if hasattr(sys.stdout, "getvalue") else "")},
        )
