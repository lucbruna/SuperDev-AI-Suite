"""
Autonomous Legal, Contract & Compliance AI Engine

Enterprise legal intelligence system providing:
- Intelligent contract analysis & generation
- Legal document management & classification
- Regulatory monitoring & compliance tracking
- Legal risk assessment & mitigation
- Automated legal auditing
- Policy creation & employee acknowledgment
- Litigation management & deadline tracking
- Confidentiality & access control
"""

from .legal_engine import LegalEngine, EngineConfig, EngineState, EngineMetrics
from .legal_manager import LegalManager, ManagerConfig
from .legal_context import LegalContext
from .legal_events import LegalEventBus, LegalEvent, EventType
from .legal_metrics import LegalMetrics, KPICalculator
from .legal_security import LegalSecurityManager
from .legal_models import *
from .legal_config import LegalConfig

from .contracts import ContractEngine, ContractAnalyzer, ClauseDetector, ObligationTracker, ContractGenerator
from .documents import LegalDocumentEngine, DocumentClassifier, DocumentSearch, DocumentSummary, ArchiveManager
from .regulations import RegulationEngine, LawMonitor, RegulationTracker, UpdateAnalyzer
from .compliance import ComplianceEngine, PolicyChecker, ControlManager, ComplianceReportEngine
from .risk import LegalRiskEngine, RiskCalculator, ImpactAnalysis, MitigationPlanner
from .audit import LegalAuditEngine, EvidenceManager, HistoryTracker, AuditReportEngine
from .policies import PolicyEngine, PolicyCreator, PolicyValidator, EmployeeAcknowledgment
from .litigation import LitigationEngine, CaseManager, DeadlineTracker, LegalPrediction

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "LegalEngine", "EngineConfig", "EngineState", "EngineMetrics",
    "LegalManager", "ManagerConfig",
    "LegalContext", "LegalEventBus", "LegalEvent", "EventType",
    "LegalMetrics", "KPICalculator", "LegalSecurityManager",
    "LegalConfig",
    "ContractEngine", "ContractAnalyzer", "ClauseDetector",
    "ObligationTracker", "ContractGenerator",
    "LegalDocumentEngine", "DocumentClassifier", "DocumentSearch",
    "DocumentSummary", "ArchiveManager",
    "RegulationEngine", "LawMonitor", "RegulationTracker", "UpdateAnalyzer",
    "ComplianceEngine", "PolicyChecker", "ControlManager", "ComplianceReportEngine",
    "LegalRiskEngine", "RiskCalculator", "ImpactAnalysis", "MitigationPlanner",
    "LegalAuditEngine", "EvidenceManager", "HistoryTracker", "AuditReportEngine",
    "PolicyEngine", "PolicyCreator", "PolicyValidator", "EmployeeAcknowledgment",
    "LitigationEngine", "CaseManager", "DeadlineTracker", "LegalPrediction",
]
