from datetime import UTC, datetime

from pydantic import BaseModel


class OrganizationCreated(BaseModel):
    org_id: str
    actor_id: str
    timestamp: datetime = datetime.now(UTC)


class OrganizationUpdated(BaseModel):
    org_id: str
    actor_id: str
    timestamp: datetime = datetime.now(UTC)


class OrganizationDeleted(BaseModel):
    org_id: str
    actor_id: str
    timestamp: datetime = datetime.now(UTC)


class MemberAdded(BaseModel):
    org_id: str
    actor_id: str
    user_id: str
    timestamp: datetime = datetime.now(UTC)


class MemberRemoved(BaseModel):
    org_id: str
    actor_id: str
    user_id: str
    timestamp: datetime = datetime.now(UTC)
