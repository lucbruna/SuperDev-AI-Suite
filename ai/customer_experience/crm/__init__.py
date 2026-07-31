"""CRM subsystem."""

from .engine import CRMEngine
from .models import (
    Account,
    Activity,
    ActivityType,
    Contact,
    ContactType,
    Opportunity,
    OpportunityStage,
)

__all__ = [
    "ContactType",
    "OpportunityStage",
    "ActivityType",
    "Account",
    "Contact",
    "Opportunity",
    "Activity",
    "CRMEngine",
]
