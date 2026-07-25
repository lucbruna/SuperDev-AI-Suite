from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import async_session_factory


async def check_database_health() -> bool:
    factory = async_session_factory()
    async with factory() as session:
        try:
            result = await session.execute(text("SELECT 1"))
            row = result.scalar_one()
            return row == 1
        except Exception:
            return False
