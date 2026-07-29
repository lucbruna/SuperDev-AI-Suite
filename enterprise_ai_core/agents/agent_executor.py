"""
Agent Executor - Executes agent tasks
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from enterprise_ai_core.models import Agent, Task, TaskStatus


class AgentExecutor:
    """Executes tasks on agents"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self._running: Dict[UUID, asyncio.Task] = {}

    async def execute(self, agent: Agent, task: Task, context: Dict) -> Dict[str, Any]:
        agent.last_heartbeat = datetime.utcnow()

        try:
            if hasattr(agent, 'execute'):
                result = await agent.execute(task, context)
            else:
                result = await self._default_execute(agent, task, context)

            return result

        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise Exception(f"Agent {agent.name} execution failed: {str(e)}")

    async def _default_execute(self, agent: Agent, task: Task, context: Dict) -> Dict[str, Any]:
        await asyncio.sleep(0.1)

        return {
            "agent": agent.name,
            "task_id": str(task.id),
            "status": "completed",
            "output": f"Processed task: {task.name}",
            "summary": f"Agent {agent.name} completed task {task.name}",
        }

    async def cancel(self, task_id: UUID) -> bool:
        task = self._running.get(task_id)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            self._running.pop(task_id, None)
            return True
        return False

    def is_running(self, task_id: UUID) -> bool:
        return task_id in self._running