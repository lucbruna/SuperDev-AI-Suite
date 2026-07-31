"""Teams subsystem (Volume 26, Fase 3): gestão de equipes.

TeamEngine orquestra times corporativos com estrutura por papéis
(Desenvolvimento, Qualidade, Segurança, Operações, Gestão, Agentes IA),
settings e atividade.
"""
from __future__ import annotations

from .team_activity import TeamActivity
from .team_engine import TeamEngine
from .team_manager import TeamManager
from .team_roles import TeamRoles
from .team_settings import TeamSettings
from .team_structure import TeamStructure

__all__ = [
    "TeamActivity",
    "TeamEngine",
    "TeamManager",
    "TeamRoles",
    "TeamSettings",
    "TeamStructure",
]
