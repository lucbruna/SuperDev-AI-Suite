from __future__ import annotations

from typing import Any


class VisualCompiler:
    def __init__(self):
        self._node_handlers: dict[str, str] = {
            "Start": "input",
            "End": "output",
            "Agent Task": "agent_node",
            "Code Execute": "python_node",
            "HTTP Request": "http_node",
            "Condition": "condition_node",
            "Loop": "loop_node",
            "Wait": "wait_node",
            "Notification": "tool_node",
            "Approval": "approval_node",
            "AI Review": "agent_node",
            "Deploy": "shell_node",
        }

    def compile(self, workflow_data: dict[str, Any]) -> dict[str, Any]:
        nodes = workflow_data.get("nodes", [])
        edges = workflow_data.get("edges", [])
        steps: list[dict[str, Any]] = []
        adjacency: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        for e in edges:
            if e["source"] in adjacency:
                adjacency[e["source"]].append(e["target"])
        node_map = {n["id"]: n for n in nodes}
        sorted_ids = self._topological_sort(adjacency)
        for node_id in sorted_ids:
            node = node_map.get(node_id)
            if not node:
                continue
            label = node.get("label", "Unknown")
            step = self._compile_node(label, node.get("config", {}))
            if step:
                steps.append(step)
        return {"steps": steps, "total_nodes": len(nodes), "total_edges": len(edges)}

    def _compile_node(self, label: str, config: dict[str, Any]) -> dict[str, Any] | None:
        handler = self._node_handlers.get(label)
        if not handler:
            return None
        step: dict[str, Any] = {"type": handler}
        if handler == "agent_node":
            step["agent"] = config.get("agent", "Executor")
            step["prompt"] = config.get("prompt", "")
            step["model"] = config.get("model", "gpt-4o")
        elif handler == "http_node":
            step["url"] = config.get("url", "")
            step["method"] = config.get("method", "GET")
            step["headers"] = config.get("headers", "{}")
        elif handler == "condition_node":
            step["field"] = config.get("field", "result")
            step["operator"] = config.get("operator", "==")
            step["value"] = config.get("value", "")
        elif handler == "loop_node":
            step["max_iterations"] = int(config.get("max_iterations", 10))
            step["collection"] = config.get("collection", "items")
        elif handler == "wait_node":
            step["duration"] = int(config.get("duration", 60))
        elif handler == "tool_node":
            step["tool"] = config.get("channel", "slack")
            step["params"] = {"message": config.get("message", "")}
        elif handler == "python_node":
            step["code"] = config.get("code", "print('Hello')")
        else:
            step["config"] = config
        return step

    def _topological_sort(self, adjacency: dict[str, list[str]]) -> list[str]:
        visited: set[str] = set()
        result: list[str] = []
        def dfs(node: str):
            if node in visited:
                return
            visited.add(node)
            for neighbor in adjacency.get(node, []):
                dfs(neighbor)
            result.append(node)
        for node in adjacency:
            dfs(node)
        return list(reversed(result))

    def to_yaml(self, workflow_data: dict[str, Any]) -> str:
        compiled = self.compile(workflow_data)
        import yaml
        return yaml.dump(compiled, default_flow_style=False)

    def to_json(self, workflow_data: dict[str, Any]) -> str:
        compiled = self.compile(workflow_data)
        import json
        return json.dumps(compiled, indent=2, default=str)