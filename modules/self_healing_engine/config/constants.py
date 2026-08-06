"""Shared constants for the Self-Healing Engine module.

Values follow the same conventions as the Digital Twin and Autonomous
Developer modules: defaults live here, overridable through ``SUPERDEV_SHE_*``
environment variables in the per-area configs.
"""
from __future__ import annotations

# Runtime data lives under <project>/.superdev/self_healing_engine/
DATA_DIR_NAME = ".superdev"
MODULE_DATA_DIR = "self_healing_engine"
DEFAULT_DB_FILE = "healing.db"
DEFAULT_SNAPSHOT_DIR = "snapshots"
DEFAULT_LOGS_DIR = "logs"
DEFAULT_MEMORY_FILE = "healing_memory.json"

# Environment prefix for every config variable of this module.
ENV_PREFIX = "SUPERDEV_SHE_"

# Severity levels used by diagnostics and incidents.
SEV_INFO = "info"
SEV_WARNING = "warning"
SEV_ERROR = "error"
SEV_CRITICAL = "critical"
SEVERITIES: tuple[str, ...] = (SEV_INFO, SEV_WARNING, SEV_ERROR, SEV_CRITICAL)

# Risk levels used by the risk policy.
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"
RISK_LEVELS: tuple[str, ...] = (RISK_LOW, RISK_MEDIUM, RISK_HIGH, RISK_CRITICAL)

# Incident lifecycle statuses.
INCIDENT_OPEN = "open"
INCIDENT_DIAGNOSING = "diagnosing"
INCIDENT_REPAIRING = "repairing"
INCIDENT_RECOVERING = "recovering"
INCIDENT_RESOLVED = "resolved"
INCIDENT_CLOSED = "closed"
INCIDENT_STATUSES: tuple[str, ...] = (
    INCIDENT_OPEN,
    INCIDENT_DIAGNOSING,
    INCIDENT_REPAIRING,
    INCIDENT_RECOVERING,
    INCIDENT_RESOLVED,
    INCIDENT_CLOSED,
)

# Repair lifecycle statuses.
REPAIR_PENDING = "pending"
REPAIR_APPROVED = "approved"
REPAIR_RUNNING = "running"
REPAIR_SUCCEEDED = "succeeded"
REPAIR_FAILED = "failed"
REPAIR_ROLLED_BACK = "rolled_back"
REPAIR_SKIPPED = "skipped"
REPAIR_STATUSES: tuple[str, ...] = (
    REPAIR_PENDING,
    REPAIR_APPROVED,
    REPAIR_RUNNING,
    REPAIR_SUCCEEDED,
    REPAIR_FAILED,
    REPAIR_ROLLED_BACK,
    REPAIR_SKIPPED,
)

# Diagnostic check kinds.
CHECK_DEPENDENCIES = "dependencies"
CHECK_API = "api"
CHECK_WORKFLOW = "workflow"
CHECK_PLUGIN = "plugin"
CHECK_DATABASE = "database"
CHECK_FILESYSTEM = "filesystem"
CHECK_SECURITY = "security"
CHECK_PERFORMANCE = "performance"
CHECK_CONFIGURATION = "configuration"
CHECK_CONSISTENCY = "consistency"
CHECK_INTEGRITY = "integrity"
CHECK_KINDS: tuple[str, ...] = (
    CHECK_DEPENDENCIES,
    CHECK_API,
    CHECK_WORKFLOW,
    CHECK_PLUGIN,
    CHECK_DATABASE,
    CHECK_FILESYSTEM,
    CHECK_SECURITY,
    CHECK_PERFORMANCE,
    CHECK_CONFIGURATION,
    CHECK_CONSISTENCY,
    CHECK_INTEGRITY,
)

# Diagnostic check outcome statuses.
CHECK_PASSED = "passed"
CHECK_WARNING = "warning"
CHECK_FAILED = "failed"
CHECK_ERROR = "error"
CHECK_SKIPPED = "skipped"
CHECK_STATUSES: tuple[str, ...] = (
    CHECK_PASSED,
    CHECK_WARNING,
    CHECK_FAILED,
    CHECK_ERROR,
    CHECK_SKIPPED,
)

# Repair kinds supported by the repair engine.
REPAIR_IMPORT = "import"
REPAIR_DEPENDENCY = "dependency"
REPAIR_CONFIGURATION = "configuration"
REPAIR_WORKFLOW = "workflow"
REPAIR_PLUGIN = "plugin"
REPAIR_DATABASE = "database"
REPAIR_API = "api"
REPAIR_FILESYSTEM = "filesystem"
REPAIR_DOCUMENTATION = "documentation"
REPAIR_KINDS: tuple[str, ...] = (
    REPAIR_IMPORT,
    REPAIR_DEPENDENCY,
    REPAIR_CONFIGURATION,
    REPAIR_WORKFLOW,
    REPAIR_PLUGIN,
    REPAIR_DATABASE,
    REPAIR_API,
    REPAIR_FILESYSTEM,
    REPAIR_DOCUMENTATION,
)

# Health statuses reported by the health score.
HEALTH_HEALTHY = "healthy"
HEALTH_DEGRADED = "degraded"
HEALTH_UNHEALTHY = "unhealthy"
HEALTH_CRITICAL = "critical"
HEALTH_STATUSES: tuple[str, ...] = (
    HEALTH_HEALTHY,
    HEALTH_DEGRADED,
    HEALTH_UNHEALTHY,
    HEALTH_CRITICAL,
)

# Pipeline phases of the healing lifecycle.
PHASE_DIAGNOSE = "diagnose"
PHASE_PLAN = "plan"
PHASE_VALIDATE = "validate"
PHASE_APPROVE = "approve"
PHASE_REPAIR = "repair"
PHASE_VERIFY = "verify"
PHASE_RECOVER = "recover"
PHASE_REPORT = "report"
PHASES: tuple[str, ...] = (
    PHASE_DIAGNOSE,
    PHASE_PLAN,
    PHASE_VALIDATE,
    PHASE_APPROVE,
    PHASE_REPAIR,
    PHASE_VERIFY,
    PHASE_RECOVER,
    PHASE_REPORT,
)

# Roles used by the permission model.
ROLE_VIEWER = "viewer"
ROLE_OPERATOR = "operator"
ROLE_ADMIN = "admin"
ROLES: tuple[str, ...] = (ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN)

# Permission keys checked by the permission model.
PERM_VIEW_HEALTH = "view_health"
PERM_RUN_DIAGNOSTICS = "run_diagnostics"
PERM_APPROVE_REPAIRS = "approve_repairs"
PERM_EXECUTE_REPAIRS = "execute_repairs"
PERM_MANAGE_ENGINE = "manage_engine"
PERMISSIONS: tuple[str, ...] = (
    PERM_VIEW_HEALTH,
    PERM_RUN_DIAGNOSTICS,
    PERM_APPROVE_REPAIRS,
    PERM_EXECUTE_REPAIRS,
    PERM_MANAGE_ENGINE,
)
