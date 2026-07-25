from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

_engine: AsyncEngine | None = None


def create_engine(
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/superdev",
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
) -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
        )
    return _engine


def get_engine_instance() -> AsyncEngine:
    if _engine is None:
        return create_engine()
    return _engine


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
