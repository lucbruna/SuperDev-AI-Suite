from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Approval:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requester: str = ""
    target_type: str = ""
    target_id: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewers: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
