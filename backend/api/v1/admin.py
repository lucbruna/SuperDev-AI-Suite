from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_admin_user

from backend.audit.audit_logger import audit_logger
from backend.database.session import get_db
from backend.security.compliance import ComplianceFramework, compliance_engine
from backend.security.multi_tenancy import TenantPlan, tenant_manager

from datetime import datetime
from typing import Optional

router = APIRouter(dependencies=[Depends(get_current_admin_user)])

# In-memory admin users store (extends the main user store)
_admin_users: list[dict] = [
    {
        "id": "1",
        "email": "admin@superdev.com",
        "fullName": "Admin User",
        "username": "admin",
        "role": "admin",
        "isActive": True,
        "isVerified": True,
        "lastLogin": "2026-07-29T00:00:00Z",
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2026-07-29T00:00:00Z",
    },
    {
        "id": "2",
        "email": "user@superdev.com",
        "fullName": "Dev User",
        "username": "devuser",
        "role": "user",
        "isActive": True,
        "isVerified": True,
        "lastLogin": "2026-07-28T12:00:00Z",
        "createdAt": "2025-06-01T00:00:00Z",
        "updatedAt": "2026-07-28T12:00:00Z",
    },
]

_admin_organizations: list[dict] = [
    {
        "id": "1",
        "name": "SuperDev",
        "slug": "superdev",
        "ownerId": "1",
        "ownerName": "Admin User",
        "memberCount": 3,
        "isActive": True,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2026-07-29T00:00:00Z",
    },
]

_admin_settings: dict = {
    "defaultLanguage": "en",
    "timezone": "UTC",
    "dateFormat": "YYYY-MM-DD",
}


class AuditQueryRequest(BaseModel):
    action: str | None = None
    resource: str | None = None
    user_id: str | None = None
    severity: str | None = None
    limit: int = 100


class TenantCreateRequest(BaseModel):
    name: str
    slug: str
    plan: str = "free"


class ComplianceCheckRequest(BaseModel):
    framework: str = "soc2"


@router.get("/audit/logs")
async def get_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> dict:
    entries = audit_logger.query(limit=limit)
    return {
        "entries": [e.to_dict() for e in entries],
        "total": len(entries),
    }


@router.get("/audit/statistics")
async def get_audit_statistics(
    db: AsyncSession = Depends(get_db),
) -> dict:


    return audit_logger.get_statistics()


@router.get("/audit/security-events")
async def get_security_events(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> dict:


    events = audit_logger.get_security_events(limit)
    return {
        "events": [e.to_dict() for e in events],
        "total": len(events),
    }


@router.get("/audit/export")
async def export_audit_logs(
    format: str = "json",
    db: AsyncSession = Depends(get_db),
):


    data = audit_logger.export(format=format)
    if format == "json":
        from fastapi.responses import JSONResponse
        return JSONResponse(content=data if isinstance(data, list) else {"data": data})
    elif format == "csv":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=data)
    return data


@router.post("/compliance/check")
async def check_compliance(
    request: ComplianceCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:


    try:
        framework = ComplianceFramework(request.framework)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown framework: {request.framework}",
        )

    report = await compliance_engine.check_compliance(framework)
    return compliance_engine.generate_report(report)


@router.get("/compliance/frameworks")
async def list_compliance_frameworks(
    db: AsyncSession = Depends(get_db),
) -> dict:


    return {
        "frameworks": [
            {"id": f.value, "name": f.value.upper()}
            for f in ComplianceFramework
        ]
    }


@router.get("/tenants")
async def list_tenants(
    db: AsyncSession = Depends(get_db),
) -> dict:


    tenants = tenant_manager.list_tenants()
    return {
        "tenants": [t.to_dict() for t in tenants],
        "total": len(tenants),
    }


@router.post("/tenants", status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from backend.dependencies import get_current_admin_user
    user = await get_current_admin_user(db=db)

    try:
        plan = TenantPlan(request.plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {request.plan}",
        )

    try:
        tenant = tenant_manager.create_tenant(
            name=request.name,
            slug=request.slug,
            owner_id=str(user.id),
            plan=plan,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return tenant.to_dict()


@router.put("/tenants/{tenant_id}/plan")
async def upgrade_tenant_plan(
    tenant_id: str,
    plan: str,
    db: AsyncSession = Depends(get_db),
) -> dict:


    try:
        new_plan = TenantPlan(plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {plan}",
        )

    tenant = tenant_manager.upgrade_plan(tenant_id, new_plan)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return tenant.to_dict()


@router.get("/users")
async def admin_list_users(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    role: str | None = None,
    isActive: bool | None = None,
    sortBy: str = "createdAt",
    sortOrder: str = "desc",
    db: AsyncSession = Depends(get_db),
):


    users = _admin_users
    if search:
        users = [u for u in users if search.lower() in u["email"].lower() or search.lower() in u["fullName"].lower()]
    if role:
        users = [u for u in users if u["role"] == role]
    if isActive is not None:
        users = [u for u in users if u["isActive"] == isActive]

    reverse = sortOrder == "desc"
    users.sort(key=lambda u: u.get(sortBy, ""), reverse=reverse)

    total = len(users)
    start = (page - 1) * limit
    items = users[start : start + limit]

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit,
    }


@router.patch("/users/{user_id}")
async def admin_update_user(
    user_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):


    for u in _admin_users:
        if u["id"] == user_id:
            for k, v in data.items():
                if k in u:
                    u[k] = v
            u["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            return {"success": True, "data": u}
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/users/{user_id}", status_code=204)
async def admin_delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):


    for i, u in enumerate(_admin_users):
        if u["id"] == user_id:
            _admin_users.pop(i)
            return None
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/organizations")
async def admin_list_organizations(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    isActive: bool | None = None,
    sortBy: str = "createdAt",
    sortOrder: str = "desc",
    db: AsyncSession = Depends(get_db),
):


    orgs = _admin_organizations
    if search:
        orgs = [o for o in orgs if search.lower() in o["name"].lower()]
    if isActive is not None:
        orgs = [o for o in orgs if o["isActive"] == isActive]

    reverse = sortOrder == "desc"
    orgs.sort(key=lambda o: o.get(sortBy, ""), reverse=reverse)

    total = len(orgs)
    start = (page - 1) * limit
    items = orgs[start : start + limit]

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit,
    }


@router.patch("/organizations/{org_id}")
async def admin_update_organization(
    org_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):


    for o in _admin_organizations:
        if o["id"] == org_id:
            for k, v in data.items():
                if k in o:
                    o[k] = v
            o["updatedAt"] = datetime.utcnow().isoformat() + "Z"
            return {"success": True, "data": o}
    raise HTTPException(status_code=404, detail="Organization not found")


@router.get("/settings")
async def admin_get_system_settings(
    db: AsyncSession = Depends(get_db),
):

    return {"success": True, "data": _admin_settings}


@router.put("/settings")
async def admin_update_system_settings(
    data: dict,
    db: AsyncSession = Depends(get_db),
):

    _admin_settings.update(data)
    return {"success": True, "data": _admin_settings}
