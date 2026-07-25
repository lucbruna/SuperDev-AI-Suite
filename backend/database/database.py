from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from backend.database.base import Base
from backend.database.engine import dispose_engine, get_engine_instance


class DatabaseConfig:
    url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/superdev"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 3600


_config = DatabaseConfig()


async def init_db(config: DatabaseConfig | None = None) -> None:
    if config is not None:
        global _config
        _config = config
    engine = create_async_engine(
        _config.url,
        echo=_config.echo,
        pool_size=_config.pool_size,
        max_overflow=_config.max_overflow,
        pool_pre_ping=_config.pool_pre_ping,
        pool_recycle=_config.pool_recycle,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


def get_engine() -> AsyncEngine:
    return get_engine_instance()


async def close_db() -> None:
    await dispose_engine()
