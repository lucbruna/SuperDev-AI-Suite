from __future__ import annotations as __

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..billing.billing_manager import BillingManager
from ..analytics.analytics_manager import AnalyticsManager
from ..feature_flags.flag_manager import FeatureFlagManager
from ..license.license_manager import LicenseManager
from ..license.license_validator import LicenseValidator
from ..compliance.compliance_manager import ComplianceManager
from ..sso.sso_manager import SSOManager
from ..monitor.enterprise_monitor import EnterpriseMonitor

router = APIRouter(prefix="/enterprise", tags=["enterprise"])


async def get_billing_manager() -> BillingManager:
    return BillingManager()


async def get_analytics_manager() -> AnalyticsManager:
    return AnalyticsManager()


async def get_flag_manager() -> FeatureFlagManager:
    return FeatureFlagManager()


async def get_license_manager() -> LicenseManager:
    return LicenseManager()


async def get_license_validator() -> LicenseValidator:
    return LicenseValidator()


async def get_compliance_manager() -> ComplianceManager:
    return ComplianceManager()


async def get_sso_manager() -> SSOManager:
    return SSOManager()


@router.post("/billing/subscribe")
async def subscribe(
    org_id: str = Query(...),
    plan: str = Query(...),
    manager: BillingManager = Depends(get_billing_manager),
):
    try:
        sub = await manager.create_subscription(org_id, plan)
        return {"subscription_id": sub.id, "plan": sub.plan.tier, "status": sub.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/billing/subscription")
async def get_subscription(
    org_id: str = Query(...),
    manager: BillingManager = Depends(get_billing_manager),
):
    sub = await manager.get_subscription(org_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub.model_dump()


@router.put("/billing/plan")
async def change_plan(
    sub_id: str = Query(...),
    new_plan: str = Query(...),
    manager: BillingManager = Depends(get_billing_manager),
):
    try:
        sub = await manager.change_plan(sub_id, new_plan)
        return {"subscription_id": sub.id, "plan": sub.plan.tier, "status": sub.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/billing/invoices")
async def list_invoices(
    org_id: str = Query(...),
    manager: BillingManager = Depends(get_billing_manager),
):
    inv_mgr = await manager.get_invoice_manager()
    invoices = await inv_mgr.list_invoices(org_id)
    return {"invoices": [inv.model_dump() for inv in invoices]}


@router.get("/analytics/dashboard")
async def get_dashboard(
    dashboard_id: str = Query("main"),
    period: str = Query("30d"),
    manager: AnalyticsManager = Depends(get_analytics_manager),
):
    data = await manager.get_dashboard_data(dashboard_id, period)
    return data.model_dump()


@router.get("/analytics/report")
async def generate_report(
    report_type: str = Query(...),
    params: Optional[str] = Query(None),
    manager: AnalyticsManager = Depends(get_analytics_manager),
):
    import json
    parsed_params = json.loads(params) if params else {}
    report = await manager.generate_report(report_type, parsed_params)
    return report.model_dump()


@router.get("/feature-flags")
async def get_feature_flags(
    user_id: str = Query(""),
    org_id: str = Query(""),
    plan_tier: str = Query("free"),
    manager: FeatureFlagManager = Depends(get_flag_manager),
):
    context = {
        "user_id": user_id,
        "org_id": org_id,
        "plan_tier": plan_tier,
    }
    flags = await manager.get_flags(context)
    return {"flags": flags}


@router.get("/license/validate")
async def validate_license(
    license_key: str = Query(...),
    manager: LicenseManager = Depends(get_license_manager),
    validator: LicenseValidator = Depends(get_license_validator),
):
    lic = await manager.validate_license(license_key)
    if not lic:
        raise HTTPException(status_code=404, detail="License not found")

    checks = validator.validate_all(lic)
    return {
        "license_key": lic.key,
        "type": lic.type,
        "valid_from": lic.valid_from.isoformat(),
        "valid_until": lic.valid_until.isoformat() if lic.valid_until else None,
        "checks": checks,
    }


@router.post("/license/activate")
async def activate_license(
    license_key: str = Query(...),
    machine_id: str = Query(...),
    manager: LicenseManager = Depends(get_license_manager),
):
    try:
        lic = await manager.activate_license(license_key, machine_id)
        return {
            "license_key": lic.key,
            "status": "activated",
            "valid_until": lic.valid_until.isoformat() if lic.valid_until else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compliance/check")
async def check_compliance(
    org_id: str = Query(...),
    standard: str = Query(...),
    manager: ComplianceManager = Depends(get_compliance_manager),
):
    try:
        report = await manager.generate_compliance_report(org_id, standard)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sso/config")
async def get_sso_config(
    provider: str = Query(...),
    redirect_uri: str = Query(""),
    manager: SSOManager = Depends(get_sso_manager),
):
    try:
        url = await manager.get_auth_url(provider, redirect_uri)
        return {"provider": provider, "auth_url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
