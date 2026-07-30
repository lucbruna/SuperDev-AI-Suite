from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConditionOperator(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    EXISTS = "exists"
    MATCHES = "matches"


@dataclass
class Condition:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field: str = ""
    operator: ConditionOperator = ConditionOperator.EQUALS
    value: Any = None
