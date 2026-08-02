"""SuperDev Ultra Harness - Next-generation agent orchestration system.

This harness provides a unified framework for specialized agent domains:
- Environment Engineering (Docker, K8s, CI/CD)
- APK/Mobile Development (Android, Flutter, React Native)
- Architecture Design (System design, Microservices, Event-driven)
- Autonomous Operations (AFK agents, self-healing, continuous ops)
- Experience/UX Engineering (UX, Design Systems, Performance)

Usage:
    from harness import UltraHarness
    harness = UltraHarness()
    await harness.initialize()
    result = await harness.execute_task("Build a microservices architecture")
"""

from .config import HarnessConfig, DomainConfig
from .agent_profiles import AgentProfile, AgentDomain, DomainProfileRegistry
from .orchestrator import UltraHarness
from .skills_registry import SkillsRegistry, SkillMapping

__version__ = "1.0.0"
__all__ = [
    "HarnessConfig",
    "DomainConfig",
    "AgentProfile",
    "AgentDomain",
    "DomainProfileRegistry",
    "UltraHarness",
    "SkillsRegistry",
    "SkillMapping",
]
