"""
Policy Validator - Validates policy definitions
"""

from typing import Any, Dict, List


class PolicyValidator:
    """Validates policy definitions"""

    def validate(self, policy: Dict) -> List[str]:
        errors = []
        if not policy.get("name"):
            errors.append("Policy must have a name")
        if not policy.get("action"):
            errors.append("Policy must have an action")
        return errors