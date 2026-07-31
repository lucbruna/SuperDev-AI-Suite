from __future__ import annotations

from enum import Enum, auto


class AgentType(Enum):
    CEO = "ceo"
    ARCHITECT = "architect"
    BACKEND = "backend"
    FRONTEND = "frontend"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    DEVOPS = "devops"
    CLOUD = "cloud"
    SECURITY = "security"
    DATABASE = "database"
    QA = "qa"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    RESEARCH = "research"
    PLANNING = "planning"
    REVIEW = "review"
    REFACTORING = "refactoring"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"
    SUPPORT = "support"
    PRODUCT = "product"
    UIUX = "uiux"
    API = "api"
    ANALYTICS = "analytics"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    TESTING = "testing"
    CODE_REVIEW = "code_review"
    CUSTOM = "custom"


class TaskPriority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class TaskStatus(Enum):
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
