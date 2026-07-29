"""
Clause Detector - Detect and classify contract clauses.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEventBus
from ..legal_models import Clause, RiskLevel
from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class ClauseDetector:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._known_clauses = {
            "auto_renewal": "Automatic renewal clause",
            "termination": "Termination clause",
            "indemnification": "Indemnification clause",
            "confidentiality": "Confidentiality clause",
            "non_compete": "Non-compete clause",
            "force_majeure": "Force majeure clause",
            "arbitration": "Arbitration clause",
            "penalty": "Penalty clause",
        }

    def detect(self, text: str) -> List[Clause]:
        found = []
        for key, name in self._known_clauses.items():
            if key.replace("_", " ") in text.lower():
                found.append(Clause(
                    id=f"CL-{key}",
                    text=name,
                    type=key,
                    risk_level=RiskLevel.LOW,
                ))
        return found

    def classify_risk(self, clause: Clause) -> RiskLevel:
        high_risk = {"penalty", "non_compete", "indemnification"}
        medium_risk = {"auto_renewal", "arbitration"}
        if clause.type in high_risk:
            return RiskLevel.HIGH
        if clause.type in medium_risk:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
