from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.passwords import hash_password, verify_password
from backend.database.models.user import User
from backend.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from backend.repositories.user_repository import UserRepository


class UserService:
    """Service layer for User business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = UserRepository(db)

    async def get_user(self, user_id: str) -> User:
        """Get a user by ID, raising not-found if missing."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        return await self.repository.get_by_email(email)

    async def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        return await self.repository.get_by_username(username)

    async def create_user(
        self,
        email: str,
        password: str,
        username: str,
        full_name: str | None = None,
    ) -> User:
        """Create a new user with hashed password."""
        # Check for existing email
        existing_email = await self.repository.get_by_email(email)
        if existing_email:
            raise UserAlreadyExistsException(field="email")

        # Check for existing username
        existing_username = await self.repository.get_by_username(username)
        if existing_username:
            raise UserAlreadyExistsException(field="username")

        hashed_password = hash_password(password)
        return await self.repository.create(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
        )

    async def update_user(self, user_id: str, **kwargs: Any) -> User:
        """Update user fields."""
        user = await self.get_user(user_id)

        # If email is being changed, check uniqueness
        if "email" in kwargs and kwargs["email"] != user.email:
            existing = await self.repository.get_by_email(kwargs["email"])
            if existing:
                raise UserAlreadyExistsException(field="email")

        # If username is being changed, check uniqueness
        if "username" in kwargs and kwargs["username"] != user.username:
            existing = await self.repository.get_by_username(kwargs["username"])
            if existing:
                raise UserAlreadyExistsException(field="username")

        updated = await self.repository.update(user_id, **kwargs)
        if not updated:
            raise UserNotFoundException()
        return updated

    async def authenticate(self, email: str, password: str) -> User:
        """Authenticate a user by email and password."""
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        if not user.is_active:
            from backend.exceptions import UserInactiveException
            raise UserInactiveException()
        return user

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[User], int]:
        """List users with optional filters."""
        return await self.repository.list(page=page, page_size=page_size, filters=filters)

    async def search_users(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        """Search users by email, username, or full name."""
        return await self.repository.search(query, page=page, page_size=page_size)

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return await self.repository.delete(user_id)
