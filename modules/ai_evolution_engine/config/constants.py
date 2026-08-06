"""Configuration constants for the AI Evolution Engine."""
from __future__ import annotations

# Pipeline phases
PHASE_ANALYZE = "analyze"
PHASE_LEARN = "learn"
PHASE_RECOMMEND = "recommend"
PHASE_FORECAST = "forecast"
PHASE_GOVERN = "govern"
PHASE_PLAN = "plan"
PHASE_REPORT = "report"

ALL_PHASES = (
    PHASE_ANALYZE,
    PHASE_LEARN,
    PHASE_RECOMMEND,
    PHASE_FORECAST,
    PHASE_GOVERN,
    PHASE_PLAN,
    PHASE_REPORT,
)

# Recommendation statuses
REC_DRAFT = "draft"
REC_PENDING = "pending"
REC_APPROVED = "approved"
REC_REJECTED = "rejected"
REC_IMPLEMENTED = "implemented"
REC_SUPERSEDED = "superseded"

# Recommendation severity levels
SEVERITY_INFO = "info"
SEVERITY_MINOR = "minor"
SEVERITY_MAJOR = "major"
SEVERITY_CRITICAL = "critical"

# Recommendation kinds
REC_ARCHITECTURE = "architecture"
REC_DEPENDENCY = "dependency"
REC_PERFORMANCE = "performance"
REC_SECURITY = "security"
REC_MODERNIZATION = "modernization"
REC_WORKFLOW = "workflow"
REC_PLUGIN = "plugin"
REC_DATABASE = "database"
REC_API = "api"

# Governance decision statuses
DECISION_PENDING = "pending"
DECISION_APPROVED = "approved"
DECISION_REJECTED = "rejected"
DECISION_ESCALATED = "escalated"

# Roadmap item statuses
ITEM_BACKLOG = "backlog"
ITEM_PLANNED = "planned"
ITEM_IN_PROGRESS = "in_progress"
ITEM_DONE = "done"
ITEM_DROPPED = "dropped"

# Analytics scope values
SCOPE_PLATFORM = "platform"
SCOPE_MODULE = "module"
SCOPE_PACKAGE = "package"
SCOPE_FILE = "file"

# Forecast horizons (in periods)
HORIZON_SHORT = 4
HORIZON_MEDIUM = 12
HORIZON_LONG = 24

# Event types
EVENT_ANALYSIS_COMPLETED = "evolution.analysis_completed"
EVENT_RECOMMENDATION_CREATED = "evolution.recommendation_created"
EVENT_RECOMMENDATION_APPROVED = "evolution.recommendation_approved"
EVENT_RECOMMENDATION_REJECTED = "evolution.recommendation_rejected"
EVENT_ROADMAP_PLANNED = "evolution.roadmap_planned"
EVENT_FORECAST_CREATED = "evolution.forecast_created"
EVENT_GOVERNANCE_DECIDED = "evolution.governance_decided"
EVENT_TICK = "evolution.tick"
