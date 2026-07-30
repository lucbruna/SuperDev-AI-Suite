from __future__ import annotations

import math
from typing import Any

from ..api_models import PaginatedResponse, PaginationParams
from ..api_interfaces import IAPIMiddleware


def paginate(
    items: list[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse:
    """Wrap a list of items into a PaginatedResponse."""
    total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def build_link_header(
    base_url: str,
    page: int,
    page_size: int,
    total_pages: int,
) -> str:
    """Build an RFC 5988 Link header for pagination."""
    links: list[str] = []
    if page > 1:
        links.append(f'<{base_url}?page={1}&page_size={page_size}>; rel="first"')
        links.append(f'<{base_url}?page={page - 1}&page_size={page_size}>; rel="prev"')
    if page < total_pages:
        links.append(f'<{base_url}?page={page + 1}&page_size={page_size}>; rel="next"')
        links.append(f'<{base_url}?page={total_pages}&page_size={page_size}>; rel="last"')
    return ", ".join(links)


class PaginationMiddleware(IAPIMiddleware):
    """Middleware that extracts pagination params from request query."""

    def __init__(self, default_page_size: int = 20, max_page_size: int = 100) -> None:
        self._default_page_size = default_page_size
        self._max_page_size = max_page_size

    async def before_request(self, request: Any) -> None:
        if not hasattr(request, "query"):
            return
        query = request.query if isinstance(request.query, dict) else {}
        page = int(query.get("page", ["1"])[0])
        page_size = int(query.get("page_size", [str(self._default_page_size)])[0])
        page = max(1, page)
        page_size = max(1, min(page_size, self._max_page_size))
        sort_by = query.get("sort_by", ["created_at"])[0]
        sort_order = query.get("sort_order", ["desc"])[0]
        params = PaginationParams(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)
        if hasattr(request, "pagination"):
            request.pagination = params

    async def after_request(self, response: Any) -> Any:
        return response

    def to_dict(self) -> dict[str, Any]:
        return {
            "middleware": "PaginationMiddleware",
            "default_page_size": self._default_page_size,
            "max_page_size": self._max_page_size,
        }
