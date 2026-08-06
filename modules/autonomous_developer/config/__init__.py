"""Configuration models for the Autonomous Developer module.

Plain dataclasses with ``SUPERDEV_AD_*`` environment overrides so the module
works with zero hard dependencies. Use :func:`get_default_config` to obtain
a fully resolved configuration rooted at the repository.
"""
from __future__ import annotations

from modules.autonomous_developer.config.coding_rules import CodingRules
from modules.autonomous_developer.config.constants import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_DB_FILE,
    DEFAULT_LOG_DIR,
    DEFAULT_REPORTS_DIR,
    DEFAULT_SESSION_FILE,
    DEFAULT_WORK_BRANCH,
    MODE_AUTONOMOUS,
    MODE_REVIEW_ONLY,
    MODE_SUPERVISED,
    MODES,
    OP_BUGFIX,
    OP_CREATE,
    OP_DELETE,
    OP_DOCUMENT,
    OP_MERGE,
    OP_MODIFY,
    OP_REFACTOR,
    OP_REVIEW,
    OP_RUN,
    OP_TEST,
    OPERATION_KINDS,
    PHASE_IMPLEMENT,
    PHASE_MERGE,
    PHASE_PLAN,
    PHASE_REVIEW,
    PHASE_TEST,
    PHASES,
    PROTECTED_PATTERNS,
    RISK_CRITICAL,
    RISK_HIGH,
    RISK_LEVELS,
    RISK_LOW,
    RISK_MEDIUM,
    TASK_BLOCKED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_IN_PROGRESS,
    TASK_PENDING,
    TASK_STATUSES,
)
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.config.permissions import (
    allowed_operations,
    check_permission,
    require_role,
)
from modules.autonomous_developer.config.planner_config import PlannerConfig
from modules.autonomous_developer.config.quality_rules import QualityRules
from modules.autonomous_developer.config.security_rules import (
    SecurityRules,
    contains_secret,
    redact_secrets,
)
from modules.autonomous_developer.config.style_rules import StyleRules


def get_default_config() -> DeveloperConfig:
    """Build a resolved default Autonomous Developer configuration."""
    config = DeveloperConfig.from_env()
    config.resolve()
    return config


__all__ = [
    "CodingRules",
    "DEFAULT_ARTIFACTS_DIR",
    "DEFAULT_DB_FILE",
    "DEFAULT_LOG_DIR",
    "DEFAULT_REPORTS_DIR",
    "DEFAULT_SESSION_FILE",
    "DEFAULT_WORK_BRANCH",
    "DeveloperConfig",
    "GeneratorConfig",
    "LLMConfig",
    "MODE_AUTONOMOUS",
    "MODE_REVIEW_ONLY",
    "MODE_SUPERVISED",
    "MODES",
    "OP_BUGFIX",
    "OP_CREATE",
    "OP_DELETE",
    "OP_DOCUMENT",
    "OP_MERGE",
    "OP_MODIFY",
    "OP_REFACTOR",
    "OP_REVIEW",
    "OP_RUN",
    "OP_TEST",
    "OPERATION_KINDS",
    "PHASE_IMPLEMENT",
    "PHASE_MERGE",
    "PHASE_PLAN",
    "PHASE_REVIEW",
    "PHASE_TEST",
    "PHASES",
    "PROTECTED_PATTERNS",
    "PlannerConfig",
    "QualityRules",
    "RISK_CRITICAL",
    "RISK_HIGH",
    "RISK_LEVELS",
    "RISK_LOW",
    "RISK_MEDIUM",
    "SecurityRules",
    "StyleRules",
    "TASK_BLOCKED",
    "TASK_COMPLETED",
    "TASK_FAILED",
    "TASK_IN_PROGRESS",
    "TASK_PENDING",
    "TASK_STATUSES",
    "allowed_operations",
    "check_permission",
    "contains_secret",
    "get_default_config",
    "redact_secrets",
    "require_role",
]
