from datetime import datetime

from pydantic import BaseModel, Field

from backend.organizations.model import OrganizationRole


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=1000)
    website: str | None = Field(None, max_length=500)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=1000)
    website: str | None = Field(None, max_length=500)
    logo_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    website: str | None
    is_active: bool
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizationList(BaseModel):
    items: list[OrganizationResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class OrganizationMemberResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InviteCreate(BaseModel):
    email: str = Field(max_length=255)
    role: OrganizationRole = OrganizationRole.MEMBER


class InviteResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    role: str
    token: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
