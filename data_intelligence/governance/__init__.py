"""Governance subsystem (Volume 22).

Access policies, data lineage, audit trail and LGPD-style compliance checks
over the data platform.
"""

from __future__ import annotations

from data_intelligence.governance.audit import AuditTrail
from data_intelligence.governance.base import (CLASSIFICATION_LEVELS,
                                               GovernanceError, PolicyRule)
from data_intelligence.governance.compliance import ComplianceChecker
from data_intelligence.governance.engine import GovernanceEngine
from data_intelligence.governance.lineage import DataLineage
from data_intelligence.governance.policy import PolicyManager

__all__ = [
    "GovernanceEngine", "PolicyManager", "PolicyRule", "DataLineage",
    "AuditTrail", "ComplianceChecker", "GovernanceError",
    "CLASSIFICATION_LEVELS",
]
