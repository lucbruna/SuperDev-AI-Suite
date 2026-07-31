"""AI Platform — public API layer over the core AI engine.

Safe imports — gracefully handles missing provider implementations.
"""
from __future__ import annotations

import importlib
import logging

logger = logging.getLogger(__name__)

# Safe re-export of core AI modules
_AI_MODULES = [
    "ai_config",
    "ai_constants",
    "ai_context",
    "ai_engine",
    "ai_exceptions",
    "ai_factory",
    "ai_interfaces",
    "ai_logger",
    "ai_manager",
    "ai_models",
    "ai_registry",
    "ai_types",
    "ai_utils",
]

for _mod_name in _AI_MODULES:
    try:
        module = importlib.import_module(f"ai.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("AI module not available: ai.%s — %s", _mod_name, e)

# Data & Analytics Engine (Volume 12) — public API for business intelligence,
# ingestion, analytics, ML, forecasting, reporting and streaming.
_DATA_MODULES = [
    "data_config",
    "data_context",
    "data_engine",
    "data_events",
    "data_factory",
    "data_logger",
    "data_manager",
    "data_metrics",
    "data_models",
    "data_registry",
    "data_runtime",
    "data_security",
]

for _mod_name in _DATA_MODULES:
    try:
        module = importlib.import_module(f"data.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Data module not available: data.%s — %s", _mod_name, e)

# Re-export the data package itself and its top-level engines so callers can
# use `from ai_platform import data` / `from ai_platform import DataEngine`.
# Bound via importlib (same pattern as _AI_MODULES) to avoid import statements
# after executable code (ruff E402).
try:
    _data_pkg = importlib.import_module("data")
    globals()["data"] = _data_pkg
    _DATA_EXPORTS = [
        "DataConfig",
        "DataEngine",
        "DataFactory",
        "DataManager",
        "AnalyticsEngine",
        "BIEngine",
        "CatalogEngine",
        "EtlEngine",
        "ForecastingEngine",
        "GovernanceEngine",
        "IngestionEngine",
        "LakeEngine",
        "MLEngine",
        "PipelineEngine",
        "ProcessingEngine",
        "QualityEngine",
        "ReportEngine",
        "StreamingEngine",
        "VisualizationEngine",
        "WarehouseEngine",
    ]
    for _name in _DATA_EXPORTS:
        _export = getattr(_data_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Data & Analytics Engine not available: %s", e)

# Testing & Quality Engine (Volume 15) — public API for automated testing,
# coverage, security scanning, benchmarking, quality scoring and the
# production gate that approves or blocks deliveries.
_QUALITY_MODULES = [
    "quality_config",
    "quality_context",
    "quality_engine",
    "quality_events",
    "quality_factory",
    "quality_logger",
    "quality_manager",
    "quality_metrics",
    "quality_models",
    "quality_registry",
    "quality_runtime",
    "quality_security",
]

for _mod_name in _QUALITY_MODULES:
    try:
        module = importlib.import_module(f"quality.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Quality module not available: quality.%s — %s", _mod_name, e)

try:
    _quality_pkg = importlib.import_module("quality")
    globals()["quality"] = _quality_pkg
    _QUALITY_EXPORTS = [
        "QualityConfig",
        "QualityEngine",
        "QualityFactory",
        "QualityManager",
        "TestingEngine",
        "UnitTestEngine",
        "IntegrationEngine",
        "RegressionEngine",
        "PerformanceEngine",
        "SecurityTestEngine",
        "AutomationEngine",
        "CoverageEngine",
        "AnalyzerEngine",
        "BenchmarkEngine",
        "QualityReportEngine",
        "ValidationEngine",
    ]
    for _name in _QUALITY_EXPORTS:
        _export = getattr(_quality_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Testing & Quality Engine not available: %s", e)

# Integration & API Engine (Volume 16) — public API for connecting external
# systems: connectors, providers, APIs, gateways, webhooks, events, messaging,
# transformation, synchronization, marketplace and monitoring.
_INTEGRATION_MODULES = [
    "integration_config",
    "integration_context",
    "integration_engine",
    "integration_events",
    "integration_factory",
    "integration_interfaces",
    "integration_logger",
    "integration_manager",
    "integration_metrics",
    "integration_models",
    "integration_protocols",
    "integration_registry",
    "integration_runtime",
    "integration_security",
]

for _mod_name in _INTEGRATION_MODULES:
    try:
        module = importlib.import_module(f"integration.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Integration module not available: integration.%s — %s",
                     _mod_name, e)

try:
    _integration_pkg = importlib.import_module("integration")
    globals()["integration"] = _integration_pkg
    _INTEGRATION_EXPORTS = [
        "IntegrationConfig",
        "IntegrationEngine",
        "IntegrationFactory",
        "IntegrationManager",
        "IntegrationRegistry",
        "IntegrationRuntime",
        "ApiEngine",
        "AuthEngine",
        "ConnectorEngine",
        "EventEngine",
        "GatewayEngine",
        "MarketplaceEngine",
        "MessagingEngine",
        "MonitoringEngine",
        "PermissionEngine",
        "SynchronizationEngine",
        "TransformationEngine",
        "WebhookEngine",
    ]
    for _name in _INTEGRATION_EXPORTS:
        _export = getattr(_integration_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Integration & API Engine not available: %s", e)

# Security Engine (Volume 16) — encryption, hashing, vault, compliance,
# threat detection, OWASP/SBOM/secrets scans and the aggregate risk score.
_SECURITY_MODULES = [
    "security_config",
    "security_context",
    "security_engine",
    "security_events",
    "security_logger",
    "security_metrics",
    "security_registry",
    "security_runtime",
    "security_security",
]
for _mod_name in _SECURITY_MODULES:
    try:
        module = importlib.import_module(f"security.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Security module not available: security.%s — %s", _mod_name, e)

try:
    _security_pkg = importlib.import_module("security")
    globals()["security"] = _security_pkg
    _SECURITY_EXPORTS = [
        "SecurityEngine",
        "SecurityConfig",
        "SecurityMetrics",
        "SecurityRegistry",
        "SecurityGuard",
        "OWASPAnalyzer",
        "SBOMGenerator",
        "SecretsDetector",
        "VulnerabilityEngine",
        "DependencyScanScanner",
        "EncryptionEngine",
        "HashingEngine",
        "SignatureEngine",
        "CertificateEngine",
        "VaultEngine",
        "SecretsEngine",
        "IntegrityEngine",
        "ComplianceEngine",
        "SecurityScanEngine",
        "ThreatDetectionEngine",
    ]
    for _name in _SECURITY_EXPORTS:
        _export = getattr(_security_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Security Engine not available: %s", e)

# DevOps & Cloud Engine (Volume 15) — public API for the DevOps lifecycle:
# build, provision, destroy, quality-gated deploys, rollback, status and
# infrastructure orchestration.
_DEVOPS_MODULES = [
    "devops_config",
    "devops_context",
    "devops_engine",
    "devops_events",
    "devops_factory",
    "devops_interfaces",
    "devops_logger",
    "devops_manager",
    "devops_metrics",
    "devops_models",
    "devops_protocols",
    "devops_registry",
    "devops_runtime",
    "devops_security",
]

for _mod_name in _DEVOPS_MODULES:
    try:
        module = importlib.import_module(f"devops.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("DevOps module not available: devops.%s — %s", _mod_name, e)

try:
    _devops_pkg = importlib.import_module("devops")
    globals()["devops"] = _devops_pkg
    _DEVOPS_EXPORTS = [
        "DevOpsEngine",
        "DevOpsConfig",
        "DevOpsContext",
        "DevOpsEvents",
        "DevOpsFactory",
        "DevOpsLogger",
        "DevOpsManager",
        "DevOpsMetrics",
        "DevOpsRegistry",
        "DevOpsRuntime",
        "DevOpsSecurity",
        "DeploymentEngine",
        "DevOpsQualityGate",
        "RollingDeployment",
        "CanaryDeployment",
        "BlueGreenDeployment",
        "DeploymentHistory",
        "DeploymentSpec",
        "DeploymentTarget",
        "DeploymentHealth",
    ]
    for _name in _DEVOPS_EXPORTS:
        _export = getattr(_devops_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("DevOps & Cloud Engine not available: %s", e)

# Autonomous Workflow & Automation Engine (Volume 20) — public API for
# creating, executing and optimizing automated business processes: workflows,
# orchestration, scheduling, triggers, actions, decisions, rules, pipelines,
# templates, monitoring and optimization.
_AUTOMATION_MODULES = [
    "automation_config",
    "automation_context",
    "automation_engine",
    "automation_events",
    "automation_factory",
    "automation_interfaces",
    "automation_logger",
    "automation_manager",
    "automation_metrics",
    "automation_models",
    "automation_protocols",
    "automation_registry",
    "automation_runtime",
    "automation_security",
]

for _mod_name in _AUTOMATION_MODULES:
    try:
        module = importlib.import_module(f"automation.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Automation module not available: automation.%s — %s",
                     _mod_name, e)

try:
    _automation_pkg = importlib.import_module("automation")
    globals()["automation"] = _automation_pkg
    _AUTOMATION_EXPORTS = [
        "ActionEngine",
        "AutomationConfig",
        "AutomationEngine",
        "AutomationFactory",
        "AutomationManager",
        "AutomationRegistry",
        "AutomationRuntime",
        "CronParser",
        "DecisionEngine",
        "DecisionTree",
        "MonitorEngine",
        "OptimizerEngine",
        "OrchestrationEngine",
        "PipelineEngine",
        "RuleEngine",
        "SchedulerEngine",
        "TemplateEngine",
        "TriggerEngine",
        "WorkflowBuilder",
        "WorkflowEngine",
    ]
    for _name in _AUTOMATION_EXPORTS:
        _export = getattr(_automation_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Autonomous Workflow & Automation Engine not available: %s", e)

# Data Intelligence & Analytics Engine (Volume 22) — public API for
# collecting, organizing and analyzing data: ingestion, pipelines,
# processing, warehouse, lake, analytics, visualization, machine learning,
# forecasting, reporting and governance.
_DATA_INTELLIGENCE_MODULES = [
    "data_config",
    "data_context",
    "data_engine",
    "data_events",
    "data_factory",
    "data_interfaces",
    "data_logger",
    "data_manager",
    "data_metrics",
    "data_models",
    "data_protocols",
    "data_registry",
    "data_runtime",
    "data_security",
]

for _mod_name in _DATA_INTELLIGENCE_MODULES:
    try:
        module = importlib.import_module(f"data_intelligence.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Data Intelligence module not available: data_intelligence.%s — %s",
                     _mod_name, e)

try:
    _data_intelligence_pkg = importlib.import_module("data_intelligence")
    globals()["data_intelligence"] = _data_intelligence_pkg
    _DATA_INTELLIGENCE_EXPORTS = [
        "AnalyticsLevel",
        "AnalyticsProvider",
        "AnalyticsResult",
        "DashboardSpec",
        "DataClassification",
        "DataConnector",
        "DataIntelligenceConfig",
        "DataIntelligenceContext",
        "DataIntelligenceEngine",
        "DataIntelligenceEventType",
        "DataIntelligenceEvents",
        "DataIntelligenceManager",
        "DataIntelligenceMetrics",
        "DataIntelligenceRegistry",
        "DataIntelligenceRuntime",
        "DataIntelligenceSecurity",
        "DataRecord",
        "DataSource",
        "DataSink",
        "GovernanceRecord",
        "ModelProvider",
        "ModelRecord",
        "ModelStatus",
        "PipelineSpec",
        "PipelineStatus",
        "PredictionResult",
        "ReportFormat",
        "ReportGenerator",
        "ReportSpec",
        "SourceType",
        "build_engine",
        "coerce_bool",
        "coerce_number",
        "new_id",
        "numeric_values",
        "safe_get",
    ]
    for _name in _DATA_INTELLIGENCE_EXPORTS:
        _export = getattr(_data_intelligence_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Data Intelligence & Analytics Engine not available: %s", e)

# Collaboration & Team Workspace Engine (Volume 26) — public API for
# workspaces where humans and AI agents collaborate: workspaces, teams,
# members, projects, tasks, comments, reviews, approvals, communication
# and knowledge.
_COLLABORATION_MODULES = [
    "collaboration_config",
    "collaboration_context",
    "collaboration_engine",
    "collaboration_events",
    "collaboration_factory",
    "collaboration_interfaces",
    "collaboration_logger",
    "collaboration_manager",
    "collaboration_metrics",
    "collaboration_models",
    "collaboration_protocols",
    "collaboration_registry",
    "collaboration_runtime",
    "collaboration_security",
]

for _mod_name in _COLLABORATION_MODULES:
    try:
        module = importlib.import_module(f"collaboration.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("Collaboration module not available: collaboration.%s — %s",
                     _mod_name, e)

try:
    _collaboration_pkg = importlib.import_module("collaboration")
    globals()["collaboration"] = _collaboration_pkg
    _COLLABORATION_EXPORTS = [
        "AgentCollaborator",
        "ApprovalFlow",
        "ApprovalRecord",
        "ApprovalStatus",
        "ChannelKind",
        "ChannelRecord",
        "CollaborationConfig",
        "CollaborationContext",
        "CollaborationEngine",
        "CollaborationEventType",
        "CollaborationEvents",
        "CollaborationManager",
        "CollaborationMetrics",
        "CollaborationRegistry",
        "CollaborationRuntime",
        "CollaborationSecurity",
        "CommentHandler",
        "CommentRecord",
        "EntityKind",
        "KnowledgeRecord",
        "KnowledgeSink",
        "MemberKind",
        "MemberRecord",
        "MemberRole",
        "MemberStatus",
        "MessageKind",
        "MessageRecord",
        "MessageSink",
        "ProjectProvider",
        "ProjectRecord",
        "ProjectStatus",
        "ReviewKind",
        "ReviewRecord",
        "ReviewStatus",
        "Reviewer",
        "TaskPriority",
        "TaskProvider",
        "TaskRecord",
        "TaskStatus",
        "TeamKind",
        "TeamProvider",
        "TeamRecord",
        "WorkspaceProvider",
        "WorkspaceRecord",
        "build_engine",
        "coerce_bool",
        "coerce_number",
        "extract_mentions",
        "get_logger",
        "new_id",
        "safe_get",
    ]
    for _name in _COLLABORATION_EXPORTS:
        _export = getattr(_collaboration_pkg, _name, None)
        if _export is not None:
            globals()[_name] = _export
except (ImportError, ModuleNotFoundError) as e:
    logger.debug("Collaboration & Team Workspace Engine not available: %s", e)
