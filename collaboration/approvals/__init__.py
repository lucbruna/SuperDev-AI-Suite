"""Approvals subsystem (Volume 26, Fase 6): aprovações em cadeia.

ApprovalEngine gerencia aprovações multi-etapa (Developer -> Tech Lead
-> Security -> Diretor) com histórico e política de quem pode aprovar.
"""
from __future__ import annotations

from .approval_engine import ApprovalEngine
from .approval_flow import ApprovalFlow
from .approval_history import ApprovalHistory
from .approval_manager import ApprovalManager
from .approval_policy import ApprovalPolicy

__all__ = [
    "ApprovalEngine",
    "ApprovalFlow",
    "ApprovalHistory",
    "ApprovalManager",
    "ApprovalPolicy",
]
