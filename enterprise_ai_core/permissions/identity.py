"""
Identity - User identity management
"""

from typing import Any, Dict
from uuid import UUID


class Identity:
    """User identity"""

    def __init__(self, user_id: UUID, roles: list = None):
        self.user_id = user_id
        self.roles = roles or []
        self.permissions = []