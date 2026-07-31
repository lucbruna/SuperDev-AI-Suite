"""Manager for deployment environments."""
from typing import List, Dict, Any, Optional
from .models import Environment, EnvironmentType


class EnvironmentManager:
    """Manages deployment environments."""

    def __init__(self):
        self._environments: Dict[str, Environment] = {}

    def create_environment(self, name: str, env_type: EnvironmentType = EnvironmentType.DEVELOPMENT,
                           url: str = "") -> Environment:
        env = Environment(name=name, environment_type=env_type, url=url)
        self._environments[env.env_id] = env
        return env

    def get_environment(self, env_id: str) -> Optional[Environment]:
        return self._environments.get(env_id)

    def get_by_name(self, name: str) -> Optional[Environment]:
        for env in self._environments.values():
            if env.name == name:
                return env
        return None

    def deactivate(self, env_id: str) -> bool:
        env = self._environments.get(env_id)
        if env:
            env.active = False
            return True
        return False

    def list_active(self) -> List[Environment]:
        return [e for e in self._environments.values() if e.active]

    def list_all(self) -> List[Environment]:
        return list(self._environments.values())

    def count(self) -> int:
        return len(self._environments)

    def get_config(self, env_id: str) -> Dict[str, Any]:
        env = self._environments.get(env_id)
        return env.config if env else {}
