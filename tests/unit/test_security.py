"""Tests for security module: compliance and multi_tenancy."""

import pytest
from backend.security.compliance import (
    ComplianceEngine,
    ComplianceFramework,
    ComplianceReport,
    ComplianceResult,
    ComplianceRule,
    ComplianceStatus,
)
from backend.security.multi_tenancy import (
    PLAN_LIMITS,
    Tenant,
    TenantLimits,
    TenantManager,
    TenantPlan,
)


# ── Compliance Enums ────────────────────────────────────────────────


class TestComplianceEnums:
    def test_framework_values(self):
        assert ComplianceFramework.SOC2.value == "soc2"
        assert ComplianceFramework.GDPR.value == "gdpr"
        assert ComplianceFramework.HIPAA.value == "hipaa"
        assert ComplianceFramework.ISO27001.value == "iso27001"
        assert ComplianceFramework.PCI_DSS.value == "pci_dss"

    def test_status_values(self):
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.NON_COMPLIANT.value == "non_compliant"
        assert ComplianceStatus.PARTIAL.value == "partial"
        assert ComplianceStatus.UNKNOWN.value == "unknown"


# ── ComplianceRule ──────────────────────────────────────────────────


class TestComplianceRule:
    def test_creation(self):
        rule = ComplianceRule(
            id="test-rule",
            framework=ComplianceFramework.SOC2,
            name="Test Rule",
            description="A test rule",
            category="security",
            check_function="check_test",
        )
        assert rule.id == "test-rule"
        assert rule.severity == "high"


# ── ComplianceEngine ────────────────────────────────────────────────


class TestComplianceEngine:
    def test_default_rules_registered(self):
        engine = ComplianceEngine()
        rules = engine.get_rules()
        assert len(rules) >= 8

    def test_get_rules_by_framework(self):
        engine = ComplianceEngine()
        soc2_rules = engine.get_rules(ComplianceFramework.SOC2)
        assert all(r.framework == ComplianceFramework.SOC2 for r in soc2_rules)
        assert len(soc2_rules) >= 3

    def test_register_custom_rule(self):
        engine = ComplianceEngine()
        custom = ComplianceRule(
            id="custom",
            framework=ComplianceFramework.HIPAA,
            name="Custom",
            description="Custom rule",
            category="security",
            check_function="check_custom",
        )
        engine.register_rule(custom)
        assert custom in engine.get_rules(ComplianceFramework.HIPAA)

    @pytest.mark.asyncio
    async def test_check_compliance_soc2(self):
        # ComplianceEngine requires an audit_logger with get_statistics()
        class MockAuditLogger:
            def get_statistics(self):
                return {"total": 0}

        engine = ComplianceEngine(audit_logger=MockAuditLogger())
        report = await engine.check_compliance(ComplianceFramework.SOC2)
        assert isinstance(report, ComplianceReport)
        assert report.framework == ComplianceFramework.SOC2
        assert report.total_rules >= 3
        assert report.overall_status in (
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.NON_COMPLIANT,
            ComplianceStatus.PARTIAL,
        )

    @pytest.mark.asyncio
    async def test_check_compliance_gdpr(self):
        engine = ComplianceEngine()
        report = await engine.check_compliance(ComplianceFramework.GDPR)
        assert report.framework == ComplianceFramework.GDPR
        assert report.total_rules >= 3

    def test_generate_report(self):
        engine = ComplianceEngine()
        report = ComplianceReport(
            id="test",
            framework=ComplianceFramework.SOC2,
            generated_at=None,
            overall_status=ComplianceStatus.COMPLIANT,
            total_rules=10,
            compliant_rules=8,
            non_compliant_rules=2,
            results=[],
        )
        from datetime import UTC, datetime
        report.generated_at = datetime.now(UTC)

        output = engine.generate_report(report)
        assert output["framework"] == "soc2"
        assert output["summary"]["total_rules"] == 10
        assert output["summary"]["compliance_rate"] == 80.0


# ── TenantPlan / TenantLimits ───────────────────────────────────────


class TestTenantPlan:
    def test_plan_values(self):
        assert TenantPlan.FREE.value == "free"
        assert TenantPlan.PRO.value == "pro"
        assert TenantPlan.ENTERPRISE.value == "enterprise"

    def test_plan_limits_exist(self):
        for plan in TenantPlan:
            assert plan in PLAN_LIMITS

    def test_free_limits(self):
        limits = PLAN_LIMITS[TenantPlan.FREE]
        assert limits.max_users == 5
        assert limits.max_projects == 3
        assert limits.sso_enabled is False

    def test_pro_limits(self):
        limits = PLAN_LIMITS[TenantPlan.PRO]
        assert limits.max_users == 25
        assert limits.sso_enabled is True
        assert limits.audit_logging is True

    def test_enterprise_limits(self):
        limits = PLAN_LIMITS[TenantPlan.ENTERPRISE]
        assert limits.max_users == 999999
        assert limits.custom_roles is True


# ── Tenant ──────────────────────────────────────────────────────────


class TestTenant:
    def test_creation(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme")
        assert tenant.plan == TenantPlan.FREE
        assert tenant.is_active is True

    def test_limits_property(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme", plan=TenantPlan.PRO)
        assert tenant.limits.max_users == 25

    def test_check_limit_within(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme")
        tenant.usage["users"] = 3
        assert tenant.check_limit("users") is True

    def test_check_limit_exceeded(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme")
        tenant.usage["users"] = 5
        assert tenant.check_limit("users") is False

    def test_check_limit_unknown_resource(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme")
        assert tenant.check_limit("unknown_resource") is True

    def test_increment_usage(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme")
        tenant.increment_usage("projects")
        tenant.increment_usage("projects")
        assert tenant.usage["projects"] == 2

    def test_to_dict(self):
        tenant = Tenant(id="t1", name="Acme", slug="acme", owner_id="u1")
        d = tenant.to_dict()
        assert d["id"] == "t1"
        assert d["name"] == "Acme"
        assert d["plan"] == "free"
        assert "limits" in d


# ── TenantManager ───────────────────────────────────────────────────


class TestTenantManager:
    def test_create_tenant(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        assert tenant.name == "Acme"
        assert tenant.owner_id == "owner1"

    def test_create_tenant_duplicate_slug(self):
        mgr = TenantManager()
        mgr.create_tenant("Acme", "acme", "owner1")
        with pytest.raises(ValueError, match="already exists"):
            mgr.create_tenant("Acme2", "acme", "owner2")

    def test_get_tenant(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        assert mgr.get_tenant(tenant.id) is tenant

    def test_get_tenant_not_found(self):
        mgr = TenantManager()
        assert mgr.get_tenant("nonexistent") is None

    def test_get_tenant_by_slug(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        assert mgr.get_tenant_by_slug("acme") is tenant

    def test_get_tenant_by_slug_not_found(self):
        mgr = TenantManager()
        assert mgr.get_tenant_by_slug("nonexistent") is None

    def test_list_tenants(self):
        mgr = TenantManager()
        mgr.create_tenant("A", "a", "u1")
        mgr.create_tenant("B", "b", "u1")
        assert len(mgr.list_tenants()) == 2

    def test_list_tenants_by_owner(self):
        mgr = TenantManager()
        mgr.create_tenant("A", "a", "u1")
        mgr.create_tenant("B", "b", "u2")
        assert len(mgr.list_tenants(owner_id="u1")) == 1

    def test_update_tenant(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        updated = mgr.update_tenant(tenant.id, name="Acme Corp")
        assert updated.name == "Acme Corp"

    def test_update_tenant_not_found(self):
        mgr = TenantManager()
        assert mgr.update_tenant("nonexistent", name="X") is None

    def test_upgrade_plan(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        upgraded = mgr.upgrade_plan(tenant.id, TenantPlan.PRO)
        assert upgraded.plan == TenantPlan.PRO

    def test_upgrade_plan_not_found(self):
        mgr = TenantManager()
        assert mgr.upgrade_plan("nonexistent", TenantPlan.PRO) is None

    def test_add_user(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        assert mgr.add_user(tenant.id, "user1") is True
        assert tenant.usage["users"] >= 1

    def test_add_user_limit_exceeded(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1", plan=TenantPlan.FREE)
        # Free plan has max 5 users, add 5 then try 6th
        for i in range(5):
            mgr.add_user(tenant.id, f"user{i}")
        assert mgr.add_user(tenant.id, "user_overflow") is False

    def test_add_user_tenant_not_found(self):
        mgr = TenantManager()
        assert mgr.add_user("nonexistent", "user1") is False

    def test_remove_user(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        mgr.add_user(tenant.id, "user1")
        assert mgr.remove_user(tenant.id, "user1") is True

    def test_remove_user_not_found(self):
        mgr = TenantManager()
        assert mgr.remove_user("nonexistent", "user1") is False

    def test_get_user_tenants(self):
        mgr = TenantManager()
        t1 = mgr.create_tenant("A", "a", "u1")
        t2 = mgr.create_tenant("B", "b", "u1")
        user_tenants = mgr.get_user_tenants("u1")
        assert len(user_tenants) == 2

    def test_check_tenant_limit(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        assert mgr.check_tenant_limit(tenant.id, "users") is True

    def test_check_tenant_limit_not_found(self):
        mgr = TenantManager()
        assert mgr.check_tenant_limit("nonexistent", "users") is False

    def test_delete_tenant(self):
        mgr = TenantManager()
        tenant = mgr.create_tenant("Acme", "acme", "owner1")
        assert mgr.delete_tenant(tenant.id) is True
        assert mgr.get_tenant(tenant.id) is None

    def test_delete_tenant_not_found(self):
        mgr = TenantManager()
        assert mgr.delete_tenant("nonexistent") is False
