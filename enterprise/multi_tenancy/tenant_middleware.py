from __future__ import annotations as __

from typing import Optional, Callable, Awaitable
from urllib.parse import urlparse

from fastapi import Request, Response, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .tenant_manager import TenantManager

TENANT_HEADER = "X-Tenant-ID"
TENANT_DOMAIN_HEADER = "X-Original-Host"


class TenantMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Callable[[Request], AwaitResponse],
        tenant_manager: TenantManager,
    ) -> None:
        super().__init__(app)
        self.tenant_manager = tenant_manager

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], AwaitResponse]
    ) -> Response:
        tenant_id = request.headers.get(TENANT_HEADER)
        if not tenant_id:
            host = request.headers.get(TENANT_DOMAIN_HEADER)
            if not host:
                host = request.url.hostname or ""

            parts = host.split(".")
            if len(parts) >= 2:
                subdomain = parts[0]
                tenant = await self.tenant_manager.get_tenant_by_domain(host)
                if tenant:
                    tenant_id = tenant.id
                else:
                    tenant_id = subdomain

        if not tenant_id:
            tenant_id = "default"

        request.state.tenant_id = tenant_id
        request.state.tenant = await self.tenant_manager.get_tenant(tenant_id)

        response = await call_next(request)
        response.headers[TENANT_HEADER] = tenant_id
        return response


async def get_current_tenant(
    request: Request,
) -> str:
    tenant_id: str | None = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant not identified")
    return tenant_id


async def get_tenant_manager(
    request: Request,
) -> TenantManager:
    tenant_manager: TenantManager | None = getattr(
        request.app.state, "tenant_manager", None
    )
    if not tenant_manager:
        raise HTTPException(status_code=500, detail="Tenant manager not configured")
    return tenant_manager


AwaitResponse = Awaitable[Response]
