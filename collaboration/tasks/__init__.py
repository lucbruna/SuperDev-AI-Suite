"""Tasks subsystem (Volume 26, Fase 4): tarefas colaborativas.

TaskEngine orquestra tarefas com prioridades, transições de status,
dependências, agendamento (humans + agentes IA) e atividade.
"""
from __future__ import annotations

from .task_activity import TaskActivity, TaskActivityLog
from .task_dependencies import TaskDependencies
from .task_engine import TaskEngine
from .task_manager import TaskManager
from .task_priorities import prioritize, priority_rank
from .task_scheduler import TaskScheduler
from .task_status import can_transition, describe, transition

__all__ = [
    "TaskActivity",
    "TaskActivityLog",
    "TaskDependencies",
    "TaskEngine",
    "TaskManager",
    "TaskScheduler",
    "can_transition",
    "describe",
    "prioritize",
    "priority_rank",
    "transition",
]
