"""AIOS agents subsystem: the standard 13-agent swarm."""
from aios.agents.agent_registry import AgentRegistry, create_default_registry
from aios.agents.agriculture import CROP_GUIDE, AgricultureAgent
from aios.agents.analytics import AnalyticsAgent
from aios.agents.avatar import AVATAR_STYLES, AvatarAgent
from aios.agents.base_agent import AgentConfig, BaseAgent
from aios.agents.developer import LANGUAGE_TEMPLATES, DeveloperAgent
from aios.agents.director import DirectorAgent
from aios.agents.finance import FinanceAgent
from aios.agents.marketing import MarketingAgent
from aios.agents.planner import PlannerAgent
from aios.agents.research import ResearchAgent
from aios.agents.security import DEFAULT_RULES, SEVERITY_ORDER, SecurityAgent
from aios.agents.testing import TestingAgent
from aios.agents.video import VideoAgent
from aios.agents.voice import VoiceAgent

DEFAULT_AGENTS = (
    "director",
    "planner",
    "research",
    "developer",
    "security",
    "testing",
    "marketing",
    "finance",
    "agriculture",
    "video",
    "voice",
    "avatar",
    "analytics",
)

__all__ = [
    "AgentRegistry",
    "create_default_registry",
    "CROP_GUIDE",
    "AgricultureAgent",
    "AnalyticsAgent",
    "AVATAR_STYLES",
    "AvatarAgent",
    "AgentConfig",
    "BaseAgent",
    "LANGUAGE_TEMPLATES",
    "DeveloperAgent",
    "DirectorAgent",
    "FinanceAgent",
    "MarketingAgent",
    "PlannerAgent",
    "ResearchAgent",
    "DEFAULT_RULES",
    "SEVERITY_ORDER",
    "SecurityAgent",
    "TestingAgent",
    "VideoAgent",
    "VoiceAgent",
    "DEFAULT_AGENTS",
]
