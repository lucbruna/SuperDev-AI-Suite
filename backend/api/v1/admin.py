from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.audit.audit_logger import audit_logger
from backend.database.session import get_db
from backend.security.compliance import ComplianceFramework, compliance_engine
from backend.security.multi_tenancy import TenantPlan, tenant_manager

router = APIRouter()


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
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

    entries = audit_logger.query(limit=limit)
    return {
        "entries": [e.to_dict() for e in entries],
        "total": len(entries),
    }


@router.get("/audit/statistics")
async def get_audit_statistics(
    db: AsyncSession = Depends(get_db),
) -> dict:
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

    return audit_logger.get_statistics()


@router.get("/audit/security-events")
async def get_security_events(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> dict:
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

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
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

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
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

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
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

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
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

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
    from backend.dependencies import get_current_admin_user
    await get_current_admin_user(db=db)

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
