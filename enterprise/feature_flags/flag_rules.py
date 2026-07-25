from __future__ import annotations as __

import random
from typing import Dict, List, Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class FlagRule(BaseModel):
    type: str = Field(
        ...,
        pattern=r"^(user_list|org_list|plan_tier|percentage|custom)$",
    )
    values: List[Any] = Field(default_factory=list)
    attribute: str = ""
    operator: str = "in"


def evaluate_rule(rule: FlagRule, context: Dict[str, Any]) -> bool:
    if rule.type == "user_list":
        user_id = context.get("user_id", "")
        return user_id in rule.values

    elif rule.type == "org_list":
        org_id = context.get("org_id", "")
        return org_id in rule.values

    elif rule.type == "plan_tier":
        plan = context.get("plan_tier", "")
        return plan in rule.values

    elif rule.type == "percentage":
        identifier = context.get("user_id", "") or context.get("org_id", "")
        if not identifier:
            return False
        hash_val = abs(hash(identifier)) % 100
        percentage = int(rule.values[0]) if rule.values else 0
        return hash_val < percentage

    elif rule.type == "custom":
        attr_value = context.get(rule.attribute)
        if rule.operator == "in":
            return attr_value in rule.values
        elif rule.operator == "eq":
            return attr_value == rule.values[0] if rule.values else False
        elif rule.operator == "gt":
            try:
                return float(attr_value) > float(rule.values[0])
            except (TypeError, ValueError):
                return False
        elif rule.operator == "lt":
            try:
                return float(attr_value) < float(rule.values[0])
            except (TypeError, ValueError):
                return False
        return False

    return False


class Flag(BaseModel):
    name: str
    description: str = ""
    enabled: bool = True
    rules: List[FlagRule] = Field(default_factory=list)
    default_value: bool = False
    id: str = Field(default_factory=lambda: f"flag_{uuid4().hex[:12]}")


def evaluate_flag(flag: Flag, context: Dict[str, Any]) -> bool:
    if not flag.enabled:
        return flag.default_value

    if not flag.rules:
        return True

    for rule in flag.rules:
        if evaluate_rule(rule, context):
            return True

    return flag.default_value
