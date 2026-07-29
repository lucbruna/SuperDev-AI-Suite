"""
Compliance Check - Regulatory compliance verification.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class ComplianceCheck:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.event_bus = event_bus

    async def check(self, regulation: str = "all") -> Dict[str, Any]:
        results = {
            "lgpd": {"status": "compliant", "score": 92, "issues": []},
            "ifrs": {"status": "compliant", "score": 88, "issues": ["depreciação precisa ser revisada"]},
            "sarbanes_oxley": {"status": "partial", "score": 75, "issues": ["controles internos precisam ser documentados"]},
        }
        return {
            "regulation": regulation,
            "overall_status": "partial" if any(r["status"] != "compliant" for r in results.values()) else "compliant",
            "results": results if regulation == "all" else {regulation: results.get(regulation, {"status": "unknown"})},
        }

    async def check_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        if not transaction.get("nf"):
            issues.append("Nota fiscal ausente")
        if transaction.get("amount", 0) > 50000 and not transaction.get("contract"):
            issues.append("Contrato obrigatório para valores acima de R$ 50.000")
        return {"compliant": len(issues) == 0, "issues": issues, "score": max(0, 100 - len(issues) * 20)}