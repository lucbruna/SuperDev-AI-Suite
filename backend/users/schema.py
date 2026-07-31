from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    username: str = Field(min_length=3, max_length=150, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str | None = Field(None, max_length=255)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=150, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str | None = Field(None, max_length=255)
    avatar_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str | None
    avatar_url: str | None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, v: object) -> str:
        return str(v)

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool
