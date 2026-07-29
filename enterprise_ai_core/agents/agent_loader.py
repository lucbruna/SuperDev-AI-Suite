"""
Agent Loader - Loads and initializes agents
"""

from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from enterprise_ai_core.models import Agent, AgentType


class AgentLoader:
    """Loads agent implementations"""

    def __init__(self):
        self._agent_classes: Dict[str, Type] = {}
        self._loaded_agents: Dict[UUID, Agent] = {}

    def register_agent_class(self, name: str, agent_class: Type) -> None:
        self._agent_classes[name] = agent_class

    async def load_agent(self, name: str, config: Dict[str, Any]) -> Optional[Agent]:
        agent_class = self._agent_classes.get(name)
        if not agent_class:
            return None

        try:
            agent = agent_class(**config)
            if hasattr(agent, 'initialize'):
                await agent.initialize()
            return agent
        except Exception:
            return None

    def get_agent_class(self, name: str) -> Optional[Type]:
        return self._agent_classes.get(name)

    def list_available(self) -> List[str]:
        return list(self._agent_classes.keys())