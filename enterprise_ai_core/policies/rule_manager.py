"""
Rule Manager - Manages business rules
"""

from typing import Any, Dict, List


class RuleManager:
    """Manages business rules"""

    def __init__(self):
        self._rules: Dict[str, Dict] = {}

    async def initialize(self) -> None:
        pass

    def add_rule(self, name: str, rule: Dict) -> None:
        self._rules[name] = rule

    def evaluate(self, rule_name: str, context: Dict) -> bool:
        rule = self._rules.get(rule_name)
        if not rule:
            return False
        return True