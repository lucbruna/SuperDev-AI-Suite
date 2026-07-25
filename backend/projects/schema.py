import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    organization_id: uuid.UUID | None = None
    template: str | None = None
    language: str = Field(default="python", max_length=50)
    framework: str | None = None
    is_public: bool = False
    tags: list[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    slug: str | None = Field(default=None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    template: str | None = None
    language: str | None = Field(default=None, max_length=50)
    framework: str | None = None
    is_archived: bool | None = None
    is_public: bool | None = None
    settings: dict | None = None
    tags: list[str] | None = None


class OwnerInfo(BaseModel):
    id: uuid.UUID
    email: str | None = None
    display_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    owner_id: uuid.UUID
    owner: OwnerInfo | None = None
    organization_id: uuid.UUID | None = None
    workspace_id: uuid.UUID | None = None
    language: str
    framework: str | None = None
    template: str | None = None
    is_archived: bool
    is_public: bool
    settings: dict
    tags: list[str]
    member_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectList(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ProjectMemberResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    created_at: datetime
    user: OwnerInfo | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectFileResponse(BaseModel):
    path: str
    content: str
    language: str = "text"