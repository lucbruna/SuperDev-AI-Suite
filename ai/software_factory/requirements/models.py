"""Data models for requirements management."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RequirementType(Enum):
    """Types of requirements."""

    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    PORTABILITY = "portability"


class Priority(Enum):
    """Requirement priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class RequirementStatus(Enum):
    """Requirement lifecycle status."""

    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


@dataclass
class Requirement:
    """Represents a single requirement."""

    requirement_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    requirement_type: RequirementType = RequirementType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    status: RequirementStatus = RequirementStatus.DRAFT
    author: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def approve(self) -> None:
        self.status = RequirementStatus.APPROVED
        self.updated_at = datetime.utcnow()

    def reject(self) -> None:
        self.status = RequirementStatus.REJECTED
        self.updated_at = datetime.utcnow()

    def is_approved(self) -> bool:
        return self.status == RequirementStatus.APPROVED


@dataclass
class RequirementSet:
    """Collection of related requirements."""

    set_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    requirements: list[Requirement] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_requirement(self, req: Requirement) -> None:
        self.requirements.append(req)

    def get_by_type(self, rtype: RequirementType) -> list[Requirement]:
        return [r for r in self.requirements if r.requirement_type == rtype]

    def get_by_priority(self, priority: Priority) -> list[Requirement]:
        return [r for r in self.requirements if r.priority == priority]

    def approved_count(self) -> int:
        return sum(1 for r in self.requirements if r.is_approved())

    def total_count(self) -> int:
        return len(self.requirements)


@dataclass
class RequirementLink:
    """Link between two requirements."""

    link_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    link_type: str = "depends_on"
    description: str = ""


@dataclass
class RequirementChange:
    """Record of a requirement change."""

    change_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    requirement_id: str = ""
    field_name: str = ""
    old_value: Any = None
    new_value: Any = None
    changed_by: str = ""
    changed_at: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""
