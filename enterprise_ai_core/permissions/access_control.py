"""
Access Control - Access control logic
"""

from typing import Any, Dict


class AccessControl:
    """Access control logic"""

    def check(self, user_id: str, resource: str, action: str) -> bool:
        return True