from math import ceil

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


class Page(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


async def paginate(
    db: AsyncSession,
    query: Select,
    page: int = 1,
    page_size: int = 20,
) -> Page:
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    pages = max(1, ceil(total / page_size))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    items = list(result.scalars().all())

    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )
