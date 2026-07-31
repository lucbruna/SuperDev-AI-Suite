"""Autonomous Software Factory Engine — Volume 32.

End-to-end software development lifecycle automation: requirements analysis,
architecture design, code generation, database management, testing, documentation,
deployment, quality assurance, and version management.
"""
from . import architecture, database, deployment, documentation, generation, quality, requirements, testing, versioning
from .factory_config import ConfigEntry, FactoryConfig
from .factory_context import FactoryContext, FactoryContextItem
from .factory_engine import (
    FactoryPhase,
    ProjectStatus,
    SoftwareFactoryEngine,
    SoftwareProject,
)
from .factory_events import FactoryEvent, FactoryEventBus, FactoryEventType
from .factory_interfaces import (
    CodeGeneratorProtocol,
    DeployerProtocol,
    DocumentationGeneratorProtocol,
    QualityReviewerProtocol,
    RequirementAnalyzerProtocol,
    TestRunnerProtocol,
)
from .factory_logger import FactoryLogger, LogEntry, LogLevel
from .factory_manager import FactoryManager, ProjectArtifact
from .factory_metrics import FactoryMetrics, MetricPoint, MetricSummary
from .factory_models import (
    ArchitecturePattern,
    CodeFile,
    DatabaseSchema,
    DatabaseType,
    DeploymentConfig,
    Language,
    TechStack,
    TestSuite,
)
from .factory_protocols import FactoryProtocols, ProtocolConfig, ProtocolType
from .factory_registry import FactoryComponent, FactoryRegistry
from .factory_runtime import FactoryRuntime, FactoryTask, TaskState
from .factory_security import FactorySecurity, SecurityCheck, SecurityIssue, SecuritySeverity
