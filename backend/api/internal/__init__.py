from fastapi import APIRouter

router = APIRouter(prefix="/api/internal")

__all__ = ["router"]