"""Dependency mapping between tasks (Volume 31)."""

from __future__ import annotations

from collections import deque

from agent_orchestration.orchestrator_models import AgentTask


class DependencyMapper:
    """Links and orders tasks by their dependencies."""

    def link_sequential(self, tasks: list[AgentTask]) -> list[AgentTask]:
        for index in range(1, len(tasks)):
            tasks[index].dependencies = [tasks[index - 1].task_id]
        return tasks

    def add_dependency(self, task: AgentTask, depends_on: AgentTask) -> None:
        if depends_on.task_id not in task.dependencies:
            task.dependencies.append(depends_on.task_id)

    def has_cycle(self, tasks: list[AgentTask]) -> bool:
        graph = {task.task_id: list(task.dependencies) for task in tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> bool:
            if task_id in visiting:
                return True
            if task_id in visited:
                return False
            visiting.add(task_id)
            for dependency in graph.get(task_id, []):
                if visit(dependency):
                    return True
            visiting.discard(task_id)
            visited.add(task_id)
            return False

        return any(visit(task_id) for task_id in graph)

    def order(self, tasks: list[AgentTask]) -> list[str]:
        in_degree = {task.task_id: len(task.dependencies)
                     for task in tasks}
        ready = deque(task_id for task_id, degree in in_degree.items()
                      if degree == 0)
        result: list[str] = []
        while ready:
            task_id = ready.popleft()
            result.append(task_id)
            for task in tasks:
                if task_id in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        ready.append(task.task_id)
        return result if len(result) == len(tasks) else []
