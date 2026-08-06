"""Shared constants for the Autonomous Developer module.

Values follow the same conventions as the AI Code Knowledge Graph module:
defaults live here, overridable through ``SUPERDEV_AD_*`` environment
variables in the per-area configs.
"""
from __future__ import annotations

# Runtime data lives under <project>/.superdev/autonomous_developer/
DATA_DIR_NAME = ".superdev"
MODULE_DATA_DIR = "autonomous_developer"
DEFAULT_DB_FILE = "autonomous_developer.db"
DEFAULT_SESSION_FILE = "sessions.json"
DEFAULT_LOG_DIR = "logs"
DEFAULT_REPORTS_DIR = "reports"
DEFAULT_ARTIFACTS_DIR = "artifacts"
DEFAULT_WORK_BRANCH = "autonomous-dev"

# Operation kinds tracked by the task engine.
OP_CREATE = "create"
OP_MODIFY = "modify"
OP_DELETE = "delete"
OP_TEST = "test"
OP_DOCUMENT = "document"
OP_REFACTOR = "refactor"
OP_BUGFIX = "bugfix"
OP_REVIEW = "review"
OP_MERGE = "merge"
OP_RUN = "run"
OPERATION_KINDS: tuple[str, ...] = (
    OP_CREATE, OP_MODIFY, OP_DELETE, OP_TEST, OP_DOCUMENT,
    OP_REFACTOR, OP_BUGFIX, OP_REVIEW, OP_MERGE, OP_RUN,
)

# Task statuses.
TASK_PENDING = "pending"
TASK_IN_PROGRESS = "in_progress"
TASK_BLOCKED = "blocked"
TASK_COMPLETED = "completed"
TASK_FAILED = "failed"
TASK_STATUSES: tuple[str, ...] = (
    TASK_PENDING, TASK_IN_PROGRESS, TASK_BLOCKED, TASK_COMPLETED, TASK_FAILED,
)

# Risk levels for planned changes.
RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"
RISK_LEVELS: tuple[str, ...] = (RISK_LOW, RISK_MEDIUM, RISK_HIGH, RISK_CRITICAL)

# Operation phases of the autonomous flow.
PHASE_PLAN = "plan"
PHASE_IMPLEMENT = "implement"
PHASE_TEST = "test"
PHASE_REVIEW = "review"
PHASE_MERGE = "merge"
PHASES: tuple[str, ...] = (PHASE_PLAN, PHASE_IMPLEMENT, PHASE_TEST, PHASE_REVIEW, PHASE_MERGE)

# Operating modes.
MODE_AUTONOMOUS = "autonomous"
MODE_SUPERVISED = "supervised"
MODE_REVIEW_ONLY = "review_only"
MODES: tuple[str, ...] = (MODE_AUTONOMOUS, MODE_SUPERVISED, MODE_REVIEW_ONLY)

# File patterns the developer must never touch without explicit permission.
PROTECTED_PATTERNS: frozenset[str] = frozenset({
    ".env", ".env.*", "*.pem", "*.key", "id_rsa*", "id_ed25519*",
    ".superdev", "node_modules", ".venv", "venv",
})
