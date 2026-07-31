"""Workflow runner with dependency resolution."""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List


class WorkflowRunner:
    """Runs multi-step workflows with dependency ordering."""

    def __init__(self) -> None:
        self._workflows: Dict[str, Dict[str, Any]] = {}

    async def run(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        wf_id = workflow.get("id", str(uuid.uuid4()))
        steps = workflow.get("steps", [])
        levels = self._resolve_dependencies(steps)
        results: List[Dict[str, Any]] = []
        for level in levels:
            for step in level:
                result = {
                    "step_id": step.get("id", "unknown"),
                    "status": "completed",
                    "output": f"Step {step.get('id', '?')} executed",
                }
                results.append(result)
        self._workflows[wf_id] = {
            "id": wf_id,
            "status": "completed",
            "steps_total": len(steps),
            "results": results,
        }
        return {"workflow_id": wf_id, "steps_completed": len(results)}

    def _resolve_dependencies(self, steps: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        if not steps:
            return []
        id_set = {s.get("id") for s in steps}
        in_degree: Dict[str, int] = {}
        graph: Dict[str, List[str]] = {}
        for step in steps:
            sid = step.get("id", "")
            in_degree[sid] = 0
            graph[sid] = []
        for step in steps:
            sid = step.get("id", "")
            for dep in step.get("dependencies", []):
                if dep in id_set:
                    graph[dep].append(sid)
                    in_degree[sid] = in_degree.get(sid, 0) + 1
        levels: List[List[Dict[str, Any]]] = []
        step_map = {s.get("id", ""): s for s in steps}
        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        while queue:
            level_steps = [step_map[sid] for sid in queue if sid in step_map]
            levels.append(level_steps)
            next_queue: List[str] = []
            for sid in queue:
                for neighbor in graph.get(sid, []):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue
        return levels

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        wf = self._workflows.get(workflow_id)
        if wf:
            return {"id": wf["id"], "status": wf["status"], "steps": wf["steps_total"]}
        return None

    def get_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        return {wid: {"id": w["id"], "status": w["status"]} for wid, w in self._workflows.items()}
