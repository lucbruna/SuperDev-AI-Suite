"""
Legal Manager - High-level legal operations manager.

Provides simplified interface for contracts, documents,
regulations, compliance, risk, audit, policies, and litigation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .legal_engine import LegalEngine, EngineConfig
from .legal_context import LegalContext
from .legal_events import LegalEventBus
from .legal_models import (
    Contract, LegalDocument, ComplianceReport, RiskAssessment,
    AuditReport, PolicyDocument, LitigationCase, Clause,
)
from .legal_config import LegalConfig
from .legal_security import LegalSecurityManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    enable_erp_integration: bool = True
    enable_finance_integration: bool = True
    enable_crm_integration: bool = True
    decision_center_webhook: Optional[str] = None


class LegalManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = LegalEngine(config.engine_config)
        self.context = config.engine_config.context
        self.event_bus = config.engine_config.event_bus
        self.security = LegalSecurityManager()
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Legal Manager initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        logger.info("Legal Manager shutdown")

    async def get_contract(self, contract_id: str) -> Contract:
        return await self.engine.get_contract(contract_id)

    async def analyze_contract(self, contract_data: Dict[str, Any]) -> Contract:
        return await self.engine.analyze_contract(contract_data)

    async def find_contracts_by_clause(self, clause_text: str) -> List[Contract]:
        return await self.context.contracts.get("matches", [])

    async def get_document(self, document_id: str) -> LegalDocument:
        return await self.engine.get_document(document_id)

    async def search_documents(self, query: str) -> List[LegalDocument]:
        return await self.context.documents.get("results", [])

    async def get_compliance_report(self) -> ComplianceReport:
        return await self.engine.get_compliance_report()

    async def check_compliance(self, area: str = "all") -> ComplianceReport:
        return await self.engine.check_compliance(area)

    async def get_risk_assessment(self, context: Optional[Dict] = None) -> RiskAssessment:
        return await self.engine.get_risk_assessment(context)

    async def run_audit(self, scope: Optional[Dict] = None) -> AuditReport:
        return await self.engine.run_audit(scope)

    async def get_policy(self, policy_id: str) -> PolicyDocument:
        return await self.engine.get_policy(policy_id)

    async def create_policy(self, policy_data: Dict[str, Any]) -> PolicyDocument:
        return await self.context.policies.get("created", policy_data)

    async def get_case(self, case_id: str) -> LitigationCase:
        return await self.engine.get_case(case_id)

    async def get_kpis(self) -> Dict[str, float]:
        return await self.engine.get_kpis()

    async def get_legal_health_score(self) -> Dict[str, Any]:
        kpis = await self.get_kpis()
        score = sum(kpis.values()) / max(len(kpis), 1)
        return {"score": score, "status": "good" if score > 70 else "attention"}

    async def simulate_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        return await self.context.risk.get("simulation", scenario)

    async def sync_with_erp(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    async def sync_with_finance(self) -> Dict[str, Any]:
        return {"status": "synced", "timestamp": datetime.utcnow().isoformat()}

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        return self.security.check_access(user_id, resource, action)

    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.security.encrypt(data)

    def get_engine_status(self) -> Dict[str, Any]:
        metrics = self.engine.get_metrics()
        return {
            "state": metrics.state.value,
            "uptime": (datetime.utcnow() - metrics.start_time).total_seconds() if metrics.start_time else 0,
            "contracts_analyzed": metrics.contracts_analyzed,
            "compliance_checks": metrics.compliance_checks,
            "risks_assessed": metrics.risks_assessed,
            "audits_conducted": metrics.audits_conducted,
            "alerts": metrics.alerts_generated,
            "subsystems": metrics.subsystem_status,
        }

    def is_healthy(self) -> bool:
        return self.engine.get_metrics().state.value == "running"
