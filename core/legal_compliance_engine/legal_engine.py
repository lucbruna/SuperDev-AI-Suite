"""
Legal AI Engine - Core orchestration engine.

Coordinates contracts, documents, regulations, compliance,
risk, audit, policies, and litigation intelligence.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .legal_context import LegalContext
from .legal_events import LegalEvent, LegalEventBus, EventType
from .legal_models import (
    Contract, LegalDocument, ComplianceReport, RiskAssessment,
    AuditReport, PolicyDocument, LitigationCase,
)
from .legal_config import LegalConfig
from .legal_metrics import KPICalculator

logger = logging.getLogger(__name__)


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    config: LegalConfig
    event_bus: LegalEventBus
    context: LegalContext
    auto_contract_review: bool = True
    compliance_monitoring_enabled: bool = True
    risk_assessment_enabled: bool = True
    auto_approval_threshold: float = 50000.0
    decision_interval_seconds: int = 600
    enable_autonomous_mode: bool = False


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    contracts_analyzed: int = 0
    documents_classified: int = 0
    regulations_monitored: int = 0
    compliance_checks: int = 0
    risks_assessed: int = 0
    audits_conducted: int = 0
    policies_created: int = 0
    cases_tracked: int = 0
    alerts_generated: int = 0
    errors: int = 0
    last_action_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class LegalEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._decision_loop_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        logger.info("Initializing Legal AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        await self._register_event_handlers()
        self.metrics.state = EngineState.RUNNING
        logger.info("Legal AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._decision_loop_task = asyncio.create_task(self._decision_loop())
        logger.info("Legal AI Engine started")

    async def stop(self) -> None:
        logger.info("Stopping Legal AI Engine...")
        self._running = False
        if self._decision_loop_task:
            self._decision_loop_task.cancel()
            try: await self._decision_loop_task
            except asyncio.CancelledError: pass
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Legal AI Engine stopped")

    async def pause(self) -> None:
        self._running = False
        self.metrics.state = EngineState.PAUSED

    async def resume(self) -> None:
        if not self._running:
            self._running = True
            self._decision_loop_task = asyncio.create_task(self._decision_loop())
            self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        from .contracts.contract_engine import ContractEngine
        from .documents.legal_document_engine import LegalDocumentEngine
        from .regulations.regulation_engine import RegulationEngine
        from .compliance.compliance_engine import ComplianceEngine
        from .risk.legal_risk_engine import LegalRiskEngine
        from .audit.legal_audit_engine import LegalAuditEngine
        from .policies.policy_engine import PolicyEngine
        from .litigation.litigation_engine import LitigationEngine

        self._subsystems = {
            "contracts": ContractEngine(self.config.config, self.config.context, self.config.event_bus),
            "documents": LegalDocumentEngine(self.config.config, self.config.context, self.config.event_bus),
            "regulations": RegulationEngine(self.config.config, self.config.context, self.config.event_bus),
            "compliance": ComplianceEngine(self.config.config, self.config.context, self.config.event_bus),
            "risk": LegalRiskEngine(self.config.config, self.config.context, self.config.event_bus),
            "audit": LegalAuditEngine(self.config.config, self.config.context, self.config.event_bus),
            "policies": PolicyEngine(self.config.config, self.config.context, self.config.event_bus),
            "litigation": LitigationEngine(self.config.config, self.config.context, self.config.event_bus),
        }
        for name, sub in self._subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _register_event_handlers(self) -> None:
        self.config.event_bus.subscribe(EventType.CONTRACT_RISK_HIGH, self._handle_contract_risk)
        self.config.event_bus.subscribe(EventType.COMPLIANCE_VIOLATION, self._handle_compliance_violation)
        self.config.event_bus.subscribe(EventType.REGULATION_CHANGED, self._handle_regulation_change)
        self.config.event_bus.subscribe(EventType.LITIGATION_DEADLINE, self._handle_litigation_deadline)

    async def _decision_loop(self) -> None:
        while self._running:
            try:
                if self.config.enable_autonomous_mode:
                    await self._make_autonomous_decisions()
                await asyncio.sleep(self.config.decision_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Decision loop error: {e}")
                self.metrics.errors += 1
                await asyncio.sleep(60)

    async def _make_autonomous_decisions(self) -> None:
        compliance = await self._subsystems["compliance"].check_all()
        if compliance.violations_count > 0:
            await self._subsystems["compliance"].generate_alert("COMPLIANCE_VIOLATION")

    async def _handle_contract_risk(self, event: LegalEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["contracts"].handle_high_risk(event.payload)

    async def _handle_compliance_violation(self, event: LegalEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["compliance"].handle_violation(event.payload)

    async def _handle_regulation_change(self, event: LegalEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["regulations"].handle_change(event.payload)

    async def _handle_litigation_deadline(self, event: LegalEvent) -> None:
        self.metrics.alerts_generated += 1
        await self._subsystems["litigation"].handle_deadline(event.payload)

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")

    async def get_contract(self, contract_id: str) -> Contract:
        return await self._subsystems["contracts"].get_contract(contract_id)

    async def get_document(self, document_id: str) -> LegalDocument:
        return await self._subsystems["documents"].get_document(document_id)

    async def get_compliance_report(self) -> ComplianceReport:
        return await self._subsystems["compliance"].get_report()

    async def get_risk_assessment(self, context: Optional[Dict] = None) -> RiskAssessment:
        return await self._subsystems["risk"].assess(context)

    async def run_audit(self, scope: Optional[Dict] = None) -> AuditReport:
        return await self._subsystems["audit"].run(scope)

    async def get_policy(self, policy_id: str) -> PolicyDocument:
        return await self._subsystems["policies"].get_policy(policy_id)

    async def get_case(self, case_id: str) -> LitigationCase:
        return await self._subsystems["litigation"].get_case(case_id)

    async def analyze_contract(self, contract_data: Dict[str, Any]) -> Contract:
        self.metrics.contracts_analyzed += 1
        return await self._subsystems["contracts"].analyze(contract_data)

    async def check_compliance(self, area: str = "all") -> ComplianceReport:
        self.metrics.compliance_checks += 1
        return await self._subsystems["compliance"].check(area)

    async def get_kpis(self) -> Dict[str, float]:
        calc = KPICalculator(self.config.context)
        return await calc.calculate_all()

    def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)
