"""Projects subsystem (Volume 26, Fase 4): gestão de projetos.

ProjectEngine orquestra projetos com fases, módulos, settings,
atividade e métricas de progresso/risco.
"""
from __future__ import annotations

from .project_activity import ProjectActivity
from .project_engine import ProjectEngine
from .project_manager import ProjectManager
from .project_metrics import ProjectMetrics
from .project_settings import ProjectSettings
from .project_structure import (DEFAULT_PHASES, ProjectStructure)

__all__ = [
    "DEFAULT_PHASES",
    "ProjectActivity",
    "ProjectEngine",
    "ProjectManager",
    "ProjectMetrics",
    "ProjectSettings",
    "ProjectStructure",
]
