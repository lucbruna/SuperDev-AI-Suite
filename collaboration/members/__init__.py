"""Members subsystem (Volume 26, Fase 3): membros humanos e agentes IA.

MemberEngine gerencia membros (kind HUMAN/AGENT), convites, perfis,
disponibilidade, permissões e atividade.
"""
from __future__ import annotations

from .activity import ActivityLog, MemberActivity
from .availability import Availability, AvailabilityManager
from .invitation import Invitation, InvitationManager
from .member_engine import MemberEngine
from .permissions import MemberPermissions
from .profile import Profile, ProfileManager

__all__ = [
    "ActivityLog",
    "Availability",
    "AvailabilityManager",
    "Invitation",
    "InvitationManager",
    "MemberActivity",
    "MemberEngine",
    "MemberPermissions",
    "Profile",
    "ProfileManager",
]
