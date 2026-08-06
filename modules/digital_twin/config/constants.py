"""Shared constants for the Digital Twin module.

Values follow the same conventions as the Autonomous Developer module:
defaults live here, overridable through ``SUPERDEV_DT_*`` environment
variables in the per-area configs.
"""
from __future__ import annotations

# Runtime data lives under <project>/.superdev/digital_twin/
DATA_DIR_NAME = ".superdev"
MODULE_DATA_DIR = "digital_twin"
DEFAULT_DB_FILE = "digital_twin.db"
DEFAULT_SNAPSHOT_DIR = "snapshots"
DEFAULT_REPORTS_DIR = "reports"
DEFAULT_LOGS_DIR = "logs"
DEFAULT_MEMORY_FILE = "twin_memory.json"

# Environment prefix for every config variable of this module.
ENV_PREFIX = "SUPERDEV_DT_"

# Synchronization kinds.
SYNC_FULL = "full"
SYNC_INCREMENTAL = "incremental"
SYNC_KINDS: tuple[str, ...] = (SYNC_FULL, SYNC_INCREMENTAL)

# Synchronization run statuses.
SYNC_PENDING = "pending"
SYNC_RUNNING = "running"
SYNC_SUCCESS = "success"
SYNC_FAILED = "failed"
SYNC_SKIPPED = "skipped"
SYNC_STATUSES: tuple[str, ...] = (
    SYNC_PENDING, SYNC_RUNNING, SYNC_SUCCESS, SYNC_FAILED, SYNC_SKIPPED,
)

# Twin state health statuses.
TWIN_SYNCED = "synced"
TWIN_OUT_OF_SYNC = "out_of_sync"
TWIN_STALE = "stale"
TWIN_STATUSES: tuple[str, ...] = (TWIN_SYNCED, TWIN_OUT_OF_SYNC, TWIN_STALE)

# Kinds of entities tracked inside the twin graph.
ENTITY_PROJECT = "project"
ENTITY_MODULE = "module"
ENTITY_SERVICE = "service"
ENTITY_WORKFLOW = "workflow"
ENTITY_PLUGIN = "plugin"
ENTITY_AGENT = "agent"
ENTITY_DATABASE = "database"
ENTITY_API = "api"
ENTITY_EVENT = "event"
ENTITY_TYPES: tuple[str, ...] = (
    ENTITY_PROJECT, ENTITY_MODULE, ENTITY_SERVICE, ENTITY_WORKFLOW,
    ENTITY_PLUGIN, ENTITY_AGENT, ENTITY_DATABASE, ENTITY_API, ENTITY_EVENT,
)

# Relationship kinds inside the twin graph.
REL_DEPENDS_ON = "depends_on"
REL_CONTAINS = "contains"
REL_MANAGES = "manages"
REL_CONNECTS = "connects"
REL_TRIGGERS = "triggers"
REL_IMPORTS = "imports"
RELATION_KINDS: tuple[str, ...] = (
    REL_DEPENDS_ON, REL_CONTAINS, REL_MANAGES, REL_CONNECTS, REL_TRIGGERS,
    REL_IMPORTS,
)

# Roles used by the permission model.
ROLE_VIEWER = "viewer"
ROLE_OPERATOR = "operator"
ROLE_ADMIN = "admin"
ROLES: tuple[str, ...] = (ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN)

# Permission keys checked by the permission model.
PERM_VIEW_TWIN = "view_twin"
PERM_RUN_SIMULATION = "run_simulation"
PERM_RUN_PREDICTION = "run_prediction"
PERM_TRIGGER_SYNC = "trigger_sync"
PERM_MANAGE_TWIN = "manage_twin"
PERMISSIONS: tuple[str, ...] = (
    PERM_VIEW_TWIN, PERM_RUN_SIMULATION, PERM_RUN_PREDICTION,
    PERM_TRIGGER_SYNC, PERM_MANAGE_TWIN,
)

# Risk levels used by simulation scenarios.
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"
RISK_LEVELS: tuple[str, ...] = (RISK_LOW, RISK_MEDIUM, RISK_HIGH, RISK_CRITICAL)

# Core phases of the twin lifecycle pipeline.
PHASE_SYNC = "sync"
PHASE_SIMULATE = "simulate"
PHASE_PREDICT = "predict"
PHASE_MONITOR = "monitor"
PHASE_REPORT = "report"
PHASES: tuple[str, ...] = (
    PHASE_SYNC, PHASE_SIMULATE, PHASE_PREDICT, PHASE_MONITOR, PHASE_REPORT,
)
