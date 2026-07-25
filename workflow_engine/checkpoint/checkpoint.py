from __future__ import annotations

import uuid
from typing import Any, Optional

from workflow_engine.graph.graph import WorkflowGraph


class CheckpointEntry:
    def __init__(self, checkpoint_id: str, workflow_id: str, graph: WorkflowGraph, context: dict[str, Any]):
        self.checkpoint_id = checkpoint_id
        self.workflow_id = workflow_id
        self.graph = graph
        self.context = context


class Checkpoint:
    def __init__(self):
        self._entries: dict[str, list[CheckpointEntry]] = {}

    async def save(self, workflow_id: str, graph_state: WorkflowGraph, context: dict[str, Any]) -> str:
        checkpoint_id = str(uuid.uuid4())
        entry = CheckpointEntry(checkpoint_id, workflow_id, graph_state, context.copy())
        self._entries.setdefault(workflow_id, []).append(entry)
        return checkpoint_id

    async def restore(self, checkpoint_id: str) -> Optional[tuple[WorkflowGraph, dict[str, Any]]]:
        for entries in self._entries.values():
            for entry in entries:
                if entry.checkpoint_id == checkpoint_id:
                    return (entry.graph, entry.context)
        return None

    async def list(self, workflow_id: str) -> list[dict[str, Any]]:
        entries = self._entries.get(workflow_id, [])
        return [
            {
                "checkpoint_id": e.checkpoint_id,
                "workflow_id": e.workflow_id,
                "node_count": len(e.graph.nodes),
            }
            for e in entries
        ]

    async def cleanup(self, workflow_id: str) -> None:
        self._entries.pop(workflow_id, None)
