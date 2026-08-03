"""SuperDev Agents — AI agent system.

Agents are the building blocks of the SuperDev AI platform, each
specializing in a specific domain like coding, reviewing, debugging, etc.

Subpackages:
- ``base``: Abstract base agent classes and interfaces
- ``core``: Core agent runtime and lifecycle
- ``registry``: Agent discovery and registration
- ``planner``: Task planning and decomposition
- ``execution``: Agent execution engine
- ``memory``: Memory and context management
- ``tools``: Agent tool registry and integrations
- ``dsl``: Agent domain-specific language
- ``debugger``: Debugging and error analysis
- ``reasoning``: Reasoning and decision-making
- ``communication``: Inter-agent messaging
- ``manager``: Agent management and supervision
- ``orchestrator``: Multi-agent orchestration
- ``agents``: Concrete agent implementations
"""
from __future__ import annotations

__version__ = "6.0.0"
__all__: list[str] = []