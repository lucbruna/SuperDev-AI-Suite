from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.users.schema import UserResponse, UserUpdate
from backend.users.service import UserService

router = APIRouter(dependencies=[Depends(get_current_active_user)])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    from backend.dependencies import get_current_active_user
    user = await get_current_active_user(db=db)
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    from backend.dependencies import get_current_active_user
    user = await get_current_active_user(db=db)
    service = UserService(db)
    updated = await service.update_user(str(user.id), **update.model_dump(exclude_unset=True))
    return UserResponse.model_validate(updated)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    service = UserService(db)
    users = await service.list_users(page=page, size=size)
    return [UserResponse.model_validate(u) for u in users]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = UserService(db)
    await service.delete_user(user_id)
