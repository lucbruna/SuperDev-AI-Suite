from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.planner")


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    FAILED = "failed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PlanStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ResourceRequirement:
    cpu_cores: float = 1.0
    memory_mb: int = 256
    disk_mb: int = 100
    gpu_required: bool = False
    network_access: bool = False
    estimated_duration_seconds: float = 60.0


@dataclass
class SubTask:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    depends_on: list[str] = field(default_factory=list)
    estimated_effort_hours: float = 1.0
    actual_effort_hours: float = 0.0
    assigned_to: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    resources: ResourceRequirement = field(default_factory=ResourceRequirement)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "depends_on": self.depends_on,
            "estimated_effort_hours": self.estimated_effort_hours,
            "actual_effort_hours": self.actual_effort_hours,
            "assigned_to": self.assigned_to,
            "metadata": self.metadata,
            "resources": {
                "cpu_cores": self.resources.cpu_cores,
                "memory_mb": self.resources.memory_mb,
                "disk_mb": self.resources.disk_mb,
                "gpu_required": self.resources.gpu_required,
                "network_access": self.resources.network_access,
                "estimated_duration_seconds": self.resources.estimated_duration_seconds,
            },
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SubTask:
        res_data = data.get("resources", {})
        resources = ResourceRequirement(
            cpu_cores=res_data.get("cpu_cores", 1.0),
            memory_mb=res_data.get("memory_mb", 256),
            disk_mb=res_data.get("disk_mb", 100),
            gpu_required=res_data.get("gpu_required", False),
            network_access=res_data.get("network_access", False),
            estimated_duration_seconds=res_data.get("estimated_duration_seconds", 60.0),
        )
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            depends_on=data.get("depends_on", []),
            estimated_effort_hours=data.get("estimated_effort_hours", 1.0),
            actual_effort_hours=data.get("actual_effort_hours", 0.0),
            assigned_to=data.get("assigned_to"),
            metadata=data.get("metadata", {}),
            resources=resources,
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            tags=data.get("tags", []),
            error=data.get("error"),
        )


@dataclass
class Task:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    title: str = ""
    description: str = ""
    goal: str = ""
    sub_tasks: list[SubTask] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "goal": self.goal,
            "sub_tasks": [st.to_dict() for st in self.sub_tasks],
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            title=data.get("title", ""),
            description=data.get("description", ""),
            goal=data.get("goal", ""),
            sub_tasks=[SubTask.from_dict(st) for st in data.get("sub_tasks", [])],
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def total_estimated_hours(self) -> float:
        return sum(st.estimated_effort_hours for st in self.sub_tasks)

    def total_actual_hours(self) -> float:
        return sum(st.actual_effort_hours for st in self.sub_tasks)

    def progress(self) -> float:
        if not self.sub_tasks:
            return 0.0
        completed = sum(1 for st in self.sub_tasks if st.status == TaskStatus.COMPLETED)
        return completed / len(self.sub_tasks)


@dataclass
class PlanValidationResult:
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    circular_dependencies: list[list[str]] = field(default_factory=list)
    orphaned_tasks: list[str] = field(default_factory=list)
    has_resource_conflicts: bool = False
    estimated_total_hours: float = 0.0


@dataclass
class Plan:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    description: str = ""
    tasks: list[Task] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Plan:
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            name=data.get("name", ""),
            description=data.get("description", ""),
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
            status=PlanStatus(data.get("status", PlanStatus.DRAFT.value)),
            version=data.get("version", "1.0.0"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(timezone.utc),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(timezone.utc),
            metadata=data.get("metadata", {}),
        )

    def total_estimated_hours(self) -> float:
        return sum(t.total_estimated_hours() for t in self.tasks)

    def total_actual_hours(self) -> float:
        return sum(t.total_actual_hours() for t in self.tasks)

    def overall_progress(self) -> float:
        if not self.tasks:
            return 0.0
        total_sub = sum(len(t.sub_tasks) for t in self.tasks)
        if total_sub == 0:
            return 0.0
        completed_sub = sum(
            sum(1 for st in t.sub_tasks if st.status == TaskStatus.COMPLETED)
            for t in self.tasks
        )
        return completed_sub / total_sub


class PlannerEngine:
    def __init__(self) -> None:
        self._plans: dict[str, Plan] = {}
        self._plan_history: dict[str, list[Plan]] = defaultdict(list)

    def create_plan(
        self,
        name: str,
        description: str = "",
        tasks: Optional[list[Task]] = None,
    ) -> Plan:
        plan = Plan(name=name, description=description, tasks=tasks or [])
        self._plans[plan.id] = plan
        logger.info("Created plan: %s (id=%s)", name, plan.id)
        return plan

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)

    def delete_plan(self, plan_id: str) -> bool:
        if plan_id in self._plans:
            del self._plans[plan_id]
            return True
        return False

    def list_plans(self, status: Optional[PlanStatus] = None) -> list[Plan]:
        if status:
            return [p for p in self._plans.values() if p.status == status]
        return list(self._plans.values())

    def decompose_task(
        self,
        title: str,
        description: str,
        goal: str,
        sub_task_specs: Optional[list[dict[str, Any]]] = None,
    ) -> Task:
        task = Task(title=title, description=description, goal=goal)

        if sub_task_specs:
            for spec in sub_task_specs:
                sub_task = SubTask(
                    name=spec.get("name", ""),
                    description=spec.get("description", ""),
                    priority=TaskPriority(spec.get("priority", TaskPriority.MEDIUM.value)),
                    depends_on=spec.get("depends_on", []),
                    estimated_effort_hours=spec.get("estimated_effort_hours", 1.0),
                    tags=spec.get("tags", []),
                )
                task.sub_tasks.append(sub_task)
        else:
            task.sub_tasks.append(
                SubTask(
                    name=f"Analyze: {title}",
                    description=f"Analysis phase for: {goal}",
                    priority=TaskPriority.HIGH,
                )
            )
            task.sub_tasks.append(
                SubTask(
                    name=f"Implement: {title}",
                    description=f"Implementation phase for: {goal}",
                    depends_on=[task.sub_tasks[0].id],
                    priority=TaskPriority.HIGH,
                )
            )
            task.sub_tasks.append(
                SubTask(
                    name=f"Verify: {title}",
                    description=f"Verification phase for: {goal}",
                    depends_on=[task.sub_tasks[1].id],
                    priority=TaskPriority.MEDIUM,
                )
            )

        return task

    def build_dependency_graph(self, plan_id: str) -> dict[str, list[str]]:
        plan = self._plans.get(plan_id)
        if not plan:
            return {}

        graph: dict[str, list[str]] = {}
        for task in plan.tasks:
            for sub in task.sub_tasks:
                graph[sub.id] = list(sub.depends_on)
        return graph

    def detect_circular_dependencies(self, plan_id: str) -> list[list[str]]:
        graph = self.build_dependency_graph(plan_id)
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            path.pop()
            rec_stack.discard(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def validate_plan(self, plan_id: str) -> PlanValidationResult:
        plan = self._plans.get(plan_id)
        result = PlanValidationResult()

        if not plan:
            result.is_valid = False
            result.errors.append("Plan not found")
            return result

        if not plan.tasks:
            result.is_valid = False
            result.errors.append("Plan has no tasks")
            return result

        all_sub_ids: set[str] = set()
        sub_to_task: dict[str, str] = {}

        for task in plan.tasks:
            for sub in task.sub_tasks:
                all_sub_ids.add(sub.id)
                sub_to_task[sub.id] = task.title

        for task in plan.tasks:
            for sub in task.sub_tasks:
                for dep in sub.depends_on:
                    if dep not in all_sub_ids:
                        result.warnings.append(
                            f"Sub-task '{sub.name}' depends on non-existent sub-task '{dep}'"
                        )

        cycles = self.detect_circular_dependencies(plan_id)
        if cycles:
            result.is_valid = False
            result.circular_dependencies = cycles
            result.errors.append(f"Circular dependencies detected: {len(cycles)} cycle(s)")

        subtask_names_in_plan: set[str] = set()
        for task in plan.tasks:
            for sub in task.sub_tasks:
                subtask_names_in_plan.add(sub.id)

        referenced_subtasks: set[str] = set()
        for task in plan.tasks:
            for sub in task.sub_tasks:
                if sub.depends_on:
                    referenced_subtasks.update(sub.depends_on)
        orphaned = subtask_names_in_plan - referenced_subtasks
        if orphaned:
            result.orphaned_tasks = list(orphaned)

        result.estimated_total_hours = plan.total_estimated_hours()

        if result.is_valid:
            plan.status = PlanStatus.VALIDATED
            logger.info("Plan '%s' validated successfully", plan.name)
        else:
            logger.warning("Plan '%s' validation failed: %s", plan.name, "; ".join(result.errors))

        return result

    def optimize_plan(self, plan_id: str) -> Plan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan '{plan_id}' not found")

        if plan.status not in (PlanStatus.DRAFT, PlanStatus.VALIDATED):
            logger.warning("Optimizing a plan that is already in progress")

        self._plan_history[plan_id].append(Plan.from_dict(plan.to_dict()))

        all_sub_tasks: list[SubTask] = []
        for task in plan.tasks:
            all_sub_tasks.extend(task.sub_tasks)

        all_sub_tasks.sort(
            key=lambda st: (
                TaskPriority.HIGH.value if st.priority == TaskPriority.CRITICAL
                else TaskPriority.HIGH.value if st.priority == TaskPriority.HIGH
                else TaskPriority.MEDIUM.value if st.priority == TaskPriority.MEDIUM
                else TaskPriority.LOW.value
            )
        )

        dependency_map: dict[str, list[SubTask]] = defaultdict(list)
        for sub in all_sub_tasks:
            for dep_id in sub.depends_on:
                dependency_map[dep_id].append(sub)

        levels: list[list[SubTask]] = []
        remaining = set(st.id for st in all_sub_tasks)
        processed: set[str] = set()

        while remaining:
            level = []
            for st_id in list(remaining):
                st = next(s for s in all_sub_tasks if s.id == st_id)
                if all(dep in processed for dep in st.depends_on):
                    level.append(st)
                    remaining.discard(st_id)

            if not level:
                break

            level.sort(key=lambda st: st.estimated_effort_hours)
            levels.append(level)
            processed.update(st.id for st in level)

        optimized_sub_tasks: list[SubTask] = []
        for level in levels:
            optimized_sub_tasks.extend(level)

        idx = 0
        for task in plan.tasks:
            task_sub_ids = set(st.id for st in task.sub_tasks)
            task.sub_tasks = [st for st in optimized_sub_tasks if st.id in task_sub_ids]
            idx += 1

        plan.updated_at = datetime.now(timezone.utc)
        logger.info("Plan '%s' optimized: %d sub-tasks reordered", plan.name, len(all_sub_tasks))

        return plan

    def estimate_completion_time(
        self, plan_id: str, parallel_workers: int = 1
    ) -> timedelta:
        plan = self._plans.get(plan_id)
        if not plan:
            return timedelta()

        graph = self.build_dependency_graph(plan_id)
        durations: dict[str, float] = {}
        for task in plan.tasks:
            for sub in task.sub_tasks:
                durations[sub.id] = sub.resources.estimated_duration_seconds

        memo: dict[str, float] = {}

        def longest_path(node: str) -> float:
            if node in memo:
                return memo[node]
            max_dep = 0.0
            for parent_id, deps in graph.items():
                if node in deps:
                    max_dep = max(max_dep, longest_path(parent_id))
            memo[node] = durations.get(node, 60.0) + max_dep
            return memo[node]

        longest = 0.0
        for node in graph:
            longest = max(longest, longest_path(node))

        return timedelta(seconds=longest / max(1, parallel_workers))

    def get_execution_order(self, plan_id: str) -> list[SubTask]:
        plan = self._plans.get(plan_id)
        if not plan:
            return []

        graph = self.build_dependency_graph(plan_id)
        visited: set[str] = set()
        order: list[SubTask] = []

        all_sub_map: dict[str, SubTask] = {}
        for task in plan.tasks:
            for sub in task.sub_tasks:
                all_sub_map[sub.id] = sub

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get(node, []):
                dfs(dep)
            if node in all_sub_map:
                order.append(all_sub_map[node])

        for node in graph:
            if node not in visited:
                dfs(node)

        return order

    def progress_report(self, plan_id: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}

        total_sub = 0
        completed_sub = 0
        in_progress_sub = 0
        blocked_sub = 0
        failed_sub = 0
        total_estimated = 0.0
        total_actual = 0.0

        for task in plan.tasks:
            for sub in task.sub_tasks:
                total_sub += 1
                total_estimated += sub.estimated_effort_hours
                total_actual += sub.actual_effort_hours
                if sub.status == TaskStatus.COMPLETED:
                    completed_sub += 1
                elif sub.status == TaskStatus.IN_PROGRESS:
                    in_progress_sub += 1
                elif sub.status == TaskStatus.BLOCKED:
                    blocked_sub += 1
                elif sub.status == TaskStatus.FAILED:
                    failed_sub += 1

        progress = (completed_sub / total_sub * 100) if total_sub > 0 else 0.0

        return {
            "plan_id": plan_id,
            "plan_name": plan.name,
            "status": plan.status.value,
            "total_tasks": len(plan.tasks),
            "total_sub_tasks": total_sub,
            "completed": completed_sub,
            "in_progress": in_progress_sub,
            "blocked": blocked_sub,
            "failed": failed_sub,
            "pending": total_sub - completed_sub - in_progress_sub - blocked_sub - failed_sub,
            "progress_percent": round(progress, 1),
            "total_estimated_hours": round(total_estimated, 2),
            "total_actual_hours": round(total_actual, 2),
            "estimated_remaining_hours": round(total_estimated - total_actual, 2),
            "estimated_completion": self.estimate_completion_time(plan_id).total_seconds(),
        }

    def serialize_plan(self, plan_id: str) -> Optional[str]:
        plan = self._plans.get(plan_id)
        if not plan:
            return None
        return json.dumps(plan.to_dict(), indent=2, default=str)

    def deserialize_plan(self, json_str: str) -> Plan:
        data = json.loads(json_str)
        plan = Plan.from_dict(data)
        self._plans[plan.id] = plan
        return plan

    def export_plan(self, plan_id: str, filepath: str) -> bool:
        serialized = self.serialize_plan(plan_id)
        if serialized is None:
            return False
        import pathlib
        pathlib.Path(filepath).write_text(serialized, encoding="utf-8")
        return True

    def import_plan(self, filepath: str) -> Optional[Plan]:
        import pathlib
        path = pathlib.Path(filepath)
        if not path.exists():
            return None
        data = path.read_text(encoding="utf-8")
        return self.deserialize_plan(data)

    def update_sub_task_status(
        self, plan_id: str, sub_task_id: str, status: TaskStatus
    ) -> bool:
        plan = self._plans.get(plan_id)
        if not plan:
            return False

        for task in plan.tasks:
            for sub in task.sub_tasks:
                if sub.id == sub_task_id:
                    sub.status = status
                    if status == TaskStatus.IN_PROGRESS:
                        sub.started_at = datetime.now(timezone.utc)
                    elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                        sub.completed_at = datetime.now(timezone.utc)
                    plan.updated_at = datetime.now(timezone.utc)
                    return True
        return False
