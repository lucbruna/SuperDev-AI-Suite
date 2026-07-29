"""
Access Policy Manager - Manages access policies
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import SecurityContext


class AccessPolicyManager:
    """Manages access policies"""

    def __init__(self, config):
        self.config = config
        self._policies: Dict[str, Dict] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def check_permission(
        self,
        context: SecurityContext,
        resource: str,
        action: str,
        resource_id: Optional[str] = None,
    ) -> bool:
        policy = self._policies.get(resource)
        if not policy:
            return True

        if "*" in context.permissions:
            return True

        required = policy.get("permissions", {}).get(action, [])
        return any(p in context.permissions for p in required)

    def add_policy(self, resource: str, policy: Dict) -> None:
        self._policies[resource] = policy

    def get_stats(self) -> Dict:
        return {"policies": len(self._policies)}