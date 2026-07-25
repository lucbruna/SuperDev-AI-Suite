from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.users.model import User
from backend.users.schema import UserCreate, UserResponse


class TestUserModel:
    def test_user_creation_with_minimal_fields(self) -> None:
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_pw",
        )
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_pw"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_verified is False
        assert user.full_name is None
        assert user.avatar_url is None

    def test_user_creation_with_all_fields(self) -> None:
        user = User(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="full@example.com",
            username="fulluser",
            hashed_password="hashed_pw",
            full_name="Full User",
            avatar_url="https://example.com/avatar.png",
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        assert user.id == "550e8400-e29b-41d4-a716-446655440000"
        assert user.full_name == "Full User"
        assert user.avatar_url == "https://example.com/avatar.png"
        assert user.is_superuser is True
        assert user.is_verified is True

    def test_user_has_tablename(self) -> None:
        assert User.__tablename__ == "users"

    def test_user_default_id_is_none(self) -> None:
        user = User(
            email="no-id@example.com",
            username="noid",
            hashed_password="pw",
        )
        assert user.id is None

    def test_user_inactive_by_default(self) -> None:
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password="pw",
            is_active=False,
        )
        assert user.is_active is False


class TestUserCreateSchema:
    def test_valid_user_create(self) -> None:
        data = UserCreate(
            email="user@example.com",
            password="securePass123",
            username="john_doe",
            full_name="John Doe",
        )
        assert data.email == "user@example.com"
        assert data.password == "securePass123"
        assert data.username == "john_doe"
        assert data.full_name == "John Doe"

    def test_user_create_without_full_name(self) -> None:
        data = UserCreate(
            email="user@example.com",
            password="securePass123",
            username="john_doe",
        )
        assert data.full_name is None

    def test_invalid_email_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",
                password="securePass123",
                username="john_doe",
            )

    def test_short_password_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="short",
                username="john_doe",
            )

    def test_long_password_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="a" * 129,
                username="john_doe",
            )

    def test_short_username_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="securePass123",
                username="ab",
            )

    def test_long_username_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="securePass123",
                username="a" * 151,
            )

    def test_username_with_special_chars_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="securePass123",
                username="user name!",
            )

    def test_username_allowed_patterns(self) -> None:
        data = UserCreate(
            email="user@example.com",
            password="securePass123",
            username="user_name_123",
        )
        assert data.username == "user_name_123"

    def test_empty_email_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            UserCreate(
                email="",
                password="securePass123",
                username="john_doe",
            )


class TestUserResponseSchema:
    def test_user_response_serialization(self) -> None:
        now = datetime.now(UTC)
        data = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="resp@example.com",
            username="respuser",
            full_name="Response User",
            avatar_url=None,
            is_active=True,
            is_superuser=False,
            is_verified=True,
            created_at=now,
            updated_at=now,
        )
        assert data.id == "550e8400-e29b-41d4-a716-446655440000"
        assert data.full_name == "Response User"
        assert data.avatar_url is None

    def test_user_response_from_attributes(self) -> None:
        assert UserResponse.model_config.get("from_attributes") is True

    def test_user_response_serializes_to_dict(self) -> None:
        now = datetime.now(UTC)
        data = UserResponse(
            id="id-1",
            email="a@b.com",
            username="auser",
            full_name=None,
            avatar_url=None,
            is_active=True,
            is_superuser=False,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )
        d = data.model_dump()
        assert d["email"] == "a@b.com"
        assert d["full_name"] is None
        assert d["is_superuser"] is False