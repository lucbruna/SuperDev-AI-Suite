from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional


class AgentSecurity:
    """Security utilities for agents."""

    @staticmethod
    def generate_token(agent_id: str, secret: str) -> str:
        raw = f"{agent_id}:{secret}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def verify_token(token: str, agent_id: str, secret: str) -> bool:
        expected = AgentSecurity.generate_token(agent_id, secret)
        return token == expected

    @staticmethod
    def sanitize_input(data: str) -> str:
        return data.strip().replace("<", "&lt;").replace(">", "&gt;")

    def to_dict(self) -> Dict[str, Any]:
        return {"security": "active"}
