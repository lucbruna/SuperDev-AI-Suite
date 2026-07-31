from backend.auth.passwords import hash_password
from backend.database.models.user import User
from backend.users.repository import UserRepository
from backend.users.schema import UserCreate, UserList, UserResponse, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = UserRepository(db)

    async def create_user(
        self,
        email: str,
        password: str,
        username: str,
        full_name: str | None = None,
    ) -> User:
        data = UserCreate(email=email, password=password, username=username, full_name=full_name)
        hashed = hash_password(password)
        return await self.repository.create(data, hashed)

    async def get_user(self, user_id: str) -> User | None:
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def get_user_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)

    async def update_user(self, user_id: str, data: UserUpdate) -> User | None:
        return await self.repository.update(user_id, data)

    async def delete_user(self, user_id: str) -> bool:
        return await self.repository.delete(user_id)

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
    ) -> UserList:
        items, total = await self.repository.list(page=page, page_size=page_size, filters=filters)
        pages = max(1, (total + page_size - 1) // page_size)
        return UserList(
            items=[UserResponse.model_validate(u) for u in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )
