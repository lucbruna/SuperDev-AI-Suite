from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.audit.audit_logger import audit_logger
from backend.database.models.organization import Organization, OrganizationMember
from backend.database.models.user import User
from backend.database.session import get_db
from backend.dependencies import get_current_admin_user
from backend.security.compliance import ComplianceFramework, compliance_engine
from backend.security.multi_tenancy import TenantPlan, tenant_manager

router = APIRouter(dependencies=[Depends(get_current_admin_user)])

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

    return {"frameworks": [{"id": f.value, "name": f.value.upper()} for f in ComplianceFramework]}


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
    sortBy: str = "created_at",
    sortOrder: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    query = select(User)
    if search:
        query = query.where(or_(User.email.ilike(f"%{search}%"), User.full_name.ilike(f"%{search}%")))
    if isActive is not None:
        query = query.where(User.is_active == isActive)

    # Count total
    count_q = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    # Sort
    sort_col = getattr(User, sortBy, User.created_at)
    order_fn = sort_col.desc() if sortOrder == "desc" else sort_col.asc()
    query = query.order_by(order_fn)

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    items = []
    for u in users:
        items.append(
            {
                "id": str(u.id),
                "email": u.email,
                "fullName": u.full_name,
                "username": u.username,
                "role": "admin" if u.is_superuser else "user",
                "isActive": u.is_active,
                "isVerified": u.is_verified,
                "lastLogin": u.last_login.isoformat() if u.last_login else None,
                "createdAt": u.created_at.isoformat() if u.created_at else None,
                "updatedAt": u.updated_at.isoformat() if u.updated_at else None,
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit if total > 0 else 1,
    }


@router.patch("/users/{user_id}")
async def admin_update_user(
    user_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for k, v in data.items():
        col = {
            "email": "email",
            "fullName": "full_name",
            "isActive": "is_active",
            "isVerified": "is_verified",
        }.get(k)
        if col and hasattr(user, col):
            setattr(user, col, v)

    await db.commit()
    return {
        "success": True,
        "data": {
            "id": str(user.id),
            "email": user.email,
            "fullName": user.full_name,
            "username": user.username,
            "isActive": user.is_active,
            "isVerified": user.is_verified,
            "updatedAt": user.updated_at.isoformat() if user.updated_at else None,
        },
    }


@router.delete("/users/{user_id}", status_code=204)
async def admin_delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return None


@router.get("/organizations")
async def admin_list_organizations(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    isActive: bool | None = None,
    sortBy: str = "created_at",
    sortOrder: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    query = select(Organization)
    if search:
        query = query.where(Organization.name.ilike(f"%{search}%"))

    count_q = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    sort_col = getattr(Organization, sortBy, Organization.created_at)
    order_fn = sort_col.desc() if sortOrder == "desc" else sort_col.asc()
    query = query.order_by(order_fn)

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    orgs = result.scalars().all()

    items = []
    for org in orgs:
        # Count members
        member_count_q = select(func.count()).select_from(
            select(OrganizationMember).where(OrganizationMember.organization_id == org.id).subquery()
        )
        mc_result = await db.execute(member_count_q)
        member_count = mc_result.scalar() or 0

        items.append(
            {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "description": org.description,
                "plan": org.plan,
                "memberCount": member_count,
                "createdAt": org.created_at.isoformat() if org.created_at else None,
                "updatedAt": org.updated_at.isoformat() if org.updated_at else None,
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit if total > 0 else 1,
    }


@router.patch("/organizations/{org_id}")
async def admin_update_organization(
    org_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    for k, v in data.items():
        col = {"name": "name", "slug": "slug", "description": "description", "plan": "plan"}.get(k)
        if col and hasattr(org, col):
            setattr(org, col, v)

    await db.commit()
    return {"success": True, "data": {"id": str(org.id), "name": org.name, "slug": org.slug}}


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
