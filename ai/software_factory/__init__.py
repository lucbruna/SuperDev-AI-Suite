"""Autonomous Software Factory Engine — Volume 32.

End-to-end software development lifecycle automation: requirements analysis,
architecture design, code generation, database management, testing, documentation,
deployment, quality assurance, and version management.
"""
from .factory_engine import (
    FactoryPhase, ProjectStatus, SoftwareProject, SoftwareFactoryEngine,
)
from .factory_manager import FactoryManager, ProjectArtifact
from .factory_runtime import FactoryRuntime, FactoryTask, TaskState
from .factory_registry import FactoryRegistry, FactoryComponent
from .factory_context import FactoryContext, FactoryContextItem
from .factory_events import FactoryEventBus, FactoryEvent, FactoryEventType
from .factory_metrics import FactoryMetrics, MetricPoint, MetricSummary
from .factory_logger import FactoryLogger, LogLevel, LogEntry
from .factory_security import FactorySecurity, SecurityCheck, SecuritySeverity, SecurityIssue
from .factory_models import (
    Language, ArchitecturePattern, DatabaseType, TechStack,
    CodeFile, DatabaseSchema, TestSuite, DeploymentConfig,
)
from .factory_interfaces import (
    RequirementAnalyzerProtocol, CodeGeneratorProtocol, TestRunnerProtocol,
    DeployerProtocol, DocumentationGeneratorProtocol, QualityReviewerProtocol,
)
from .factory_protocols import FactoryProtocols, ProtocolType, ProtocolConfig
from .factory_config import FactoryConfig, ConfigEntry

from . import requirements
from . import architecture
from . import generation
from . import database
from . import testing
from . import documentation
from . import deployment
from . import quality
from . import versioning
