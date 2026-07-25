from datetime import datetime, timezone

from pydantic import BaseModel


class OrganizationCreated(BaseModel):
    org_id: str
    actor_id: str
    timestamp: datetime = datetime.now(timezone.utc)


class OrganizationUpdated(BaseModel):
    org_id: str
    actor_id: str
    timestamp: datetime = datetime.now(timezone.utc)


class OrganizationDeleted(BaseModel):
    org_id: str
    actor_id: str
    timestamp: datetime = datetime.now(timezone.utc)


class MemberAdded(BaseModel):
    org_id: str
    actor_id: str
    user_id: str
    timestamp: datetime = datetime.now(timezone.utc)


class MemberRemoved(BaseModel):
    org_id: str
    actor_id: str
    user_id: str
    timestamp: datetime = datetime.now(timezone.utc)
