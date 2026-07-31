"""SuperDev AI Agent Orchestration Engine — Volume 13."""
from __future__ import annotations

# --- Pre-existing modules ---
from . import architect_agent
from . import base
from . import collaboration
from . import communication
from . import coordination
from . import deployment_agent
from . import documentation_agent
from . import monitoring_agent
from . import qa_agent
from . import frontend_agent
from . import database_agent
from . import security_agent

# --- Core infrastructure ---
from . import agent_config
from . import agent_engine
from . import agent_manager
from . import agent_factory
from . import agent_registry
from . import agent_runtime
from . import agent_context
from . import agent_events
from . import agent_metrics
from . import agent_logger
from . import agent_security
from . import agent_models
from . import agent_interfaces
from . import agent_protocols

# --- Volume 13 subsystems ---
from . import creation
from . import lifecycle
from . import memory
from . import planning
from . import reasoning
from . import execution
from . import evaluation
from . import learning
from . import optimization
from . import personality
from . import skills
from . import tools
from . import marketplace

__all__ = [
    # Pre-existing
    "architect_agent",
    "base",
    "collaboration",
    "communication",
    "coordination",
    "deployment_agent",
    "documentation_agent",
    "monitoring_agent",
    "qa_agent",
    "frontend_agent",
    "database_agent",
    "security_agent",
    # Core infrastructure
    "agent_config",
    "agent_engine",
    "agent_manager",
    "agent_factory",
    "agent_registry",
    "agent_runtime",
    "agent_context",
    "agent_events",
    "agent_metrics",
    "agent_logger",
    "agent_security",
    "agent_models",
    "agent_interfaces",
    "agent_protocols",
    # Volume 13 subsystems
    "creation",
    "lifecycle",
    "memory",
    "planning",
    "reasoning",
    "execution",
    "evaluation",
    "learning",
    "optimization",
    "personality",
    "skills",
    "tools",
    "marketplace",
]
