from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import JWTManager
from backend.database.session import get_db
from backend.users.model import User
from backend.users.repository import UserRepository

security = HTTPBearer(auto_error=False)
jwt_manager = JWTManager()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = jwt_manager.decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    repository = UserRepository(db)
    user = await repository.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


class AuthMiddleware:
    def __init__(self, excluded_paths: list[str] | None = None) -> None:
        self.excluded_paths = excluded_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/health",
            "/api/v1/health/ready",
            "/api/v1/health/alive",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def __call__(self, request: Request, call_next: Any) -> Any:
        from starlette.responses import JSONResponse

        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
            )

        token = auth_header.removeprefix("Bearer ")
        payload = jwt_manager.decode_token(token)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        request.state.user_id = payload.get("sub")
        return await call_next(request)
