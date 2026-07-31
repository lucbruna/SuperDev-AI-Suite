from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from backend.audit.audit_logger import AuditLogger
from backend.utils.uuid_utils import generate_uuid


class ComplianceFramework(StrEnum):
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"


class ComplianceStatus(StrEnum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass
class ComplianceRule:
    id: str
    framework: ComplianceFramework
    name: str
    description: str
    category: str
    check_function: str
    severity: str = "high"


@dataclass
class ComplianceResult:
    rule_id: str
    rule_name: str
    framework: ComplianceFramework
    status: ComplianceStatus
    details: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ComplianceReport:
    id: str
    framework: ComplianceFramework
    generated_at: datetime
    overall_status: ComplianceStatus
    total_rules: int
    compliant_rules: int
    non_compliant_rules: int
    results: list[ComplianceResult] = field(default_factory=list)


class ComplianceEngine:
    """Enterprise compliance checking engine."""

    def __init__(self, audit_logger: AuditLogger | None = None):
        self._audit_logger = audit_logger or AuditLogger()
        self._rules: dict[str, ComplianceRule] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        default_rules = [
            ComplianceRule(
                id="soc2-access-control",
                framework=ComplianceFramework.SOC2,
                name="Access Control Logging",
                description="All access attempts must be logged",
                category="access_control",
                check_function="check_access_logging",
                severity="high",
            ),
            ComplianceRule(
                id="soc2-password-policy",
                framework=ComplianceFramework.SOC2,
                name="Password Policy",
                description="Passwords must meet minimum complexity requirements",
                category="security",
                check_function="check_password_policy",
                severity="high",
            ),
            ComplianceRule(
                id="soc2-session-management",
                framework=ComplianceFramework.SOC2,
                name="Session Management",
                description="Sessions must have appropriate timeouts",
                category="security",
                check_function="check_session_management",
                severity="medium",
            ),
            ComplianceRule(
                id="gdpr-data-access",
                framework=ComplianceFramework.GDPR,
                name="Data Access Rights",
                description="Users must be able to export their data",
                category="data_protection",
                check_function="check_data_access_rights",
                severity="high",
            ),
            ComplianceRule(
                id="gdpr-data-deletion",
                framework=ComplianceFramework.GDPR,
                name="Right to Erasure",
                description="Users must be able to delete their data",
                category="data_protection",
                check_function="check_data_deletion_rights",
                severity="high",
            ),
            ComplianceRule(
                id="gdpr-consent",
                framework=ComplianceFramework.GDPR,
                name="Consent Management",
                description="User consent must be recorded and manageable",
                category="data_protection",
                check_function="check_consent_management",
                severity="medium",
            ),
            ComplianceRule(
                id="iso-audit-logging",
                framework=ComplianceFramework.ISO27001,
                name="Audit Logging",
                description="System events must be logged with timestamps",
                category="audit",
                check_function="check_audit_logging",
                severity="high",
            ),
            ComplianceRule(
                id="iso-access-review",
                framework=ComplianceFramework.ISO27001,
                name="Access Review",
                description="User access must be reviewed periodically",
                category="access_control",
                check_function="check_access_review",
                severity="medium",
            ),
        ]

        for rule in default_rules:
            self._rules[rule.id] = rule

    def register_rule(self, rule: ComplianceRule) -> None:
        self._rules[rule.id] = rule

    def get_rules(self, framework: ComplianceFramework | None = None) -> list[ComplianceRule]:
        rules = list(self._rules.values())
        if framework:
            rules = [r for r in rules if r.framework == framework]
        return rules

    async def check_compliance(
        self,
        framework: ComplianceFramework,
        context: dict[str, Any] | None = None,
    ) -> ComplianceReport:
        rules = self.get_rules(framework)
        results: list[ComplianceResult] = []

        for rule in rules:
            status = await self._evaluate_rule(rule, context or {})
            results.append(
                ComplianceResult(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    framework=framework,
                    status=status,
                    details=f"Checked: {rule.description}",
                )
            )

        compliant = sum(1 for r in results if r.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for r in results if r.status == ComplianceStatus.NON_COMPLIANT)
        total = len(results)

        if non_compliant == 0:
            overall = ComplianceStatus.COMPLIANT
        elif compliant == 0:
            overall = ComplianceStatus.NON_COMPLIANT
        else:
            overall = ComplianceStatus.PARTIAL

        return ComplianceReport(
            id=generate_uuid(),
            framework=framework,
            generated_at=datetime.now(UTC),
            overall_status=overall,
            total_rules=total,
            compliant_rules=compliant,
            non_compliant_rules=non_compliant,
            results=results,
        )

    async def _evaluate_rule(
        self,
        rule: ComplianceRule,
        context: dict[str, Any],
    ) -> ComplianceStatus:
        checks = {
            "check_access_logging": self._check_access_logging,
            "check_password_policy": self._check_password_policy,
            "check_session_management": self._check_session_management,
            "check_data_access_rights": self._check_data_access_rights,
            "check_data_deletion_rights": self._check_data_deletion_rights,
            "check_consent_management": self._check_consent_management,
            "check_audit_logging": self._check_audit_logging,
            "check_access_review": self._check_access_review,
        }

        check_fn = checks.get(rule.check_function)
        if check_fn:
            return await check_fn(context)
        return ComplianceStatus.UNKNOWN

    async def _check_access_logging(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify access attempts are being logged."""
        stats = self._audit_logger.get_statistics()
        total = stats.get("total", 0)
        if total == 0:
            return ComplianceStatus.NON_COMPLIANT
        # Check that login/logout events are actually present
        actions = stats.get("by_action", {})
        has_access_events = any(action in actions for action in ("login", "logout", "login_failed"))
        if has_access_events and total > 0:
            return ComplianceStatus.COMPLIANT
        if total > 0:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    async def _check_password_policy(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify password policy is enforced.

        Checks context for ``password_min_length`` (default 8) and
        ``password_require_special`` (default True).
        """
        min_length = context.get("password_min_length", 8)
        require_special = context.get("password_require_special", True)

        if min_length >= 8 and require_special:
            return ComplianceStatus.COMPLIANT
        if min_length >= 6:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    async def _check_session_management(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify sessions have appropriate timeouts and cookie flags."""
        session_ttl = context.get("session_ttl_seconds", 3600)
        cookie_secure = context.get("session_cookie_secure", True)
        cookie_httponly = context.get("session_cookie_httponly", True)

        compliant = True
        if session_ttl > 86400:  # more than 24h is excessive
            compliant = False
        if not cookie_secure:
            compliant = False
        if not cookie_httponly:
            compliant = False

        if compliant:
            return ComplianceStatus.COMPLIANT
        # Partial if at least some controls are in place
        if session_ttl <= 86400:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    async def _check_data_access_rights(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify data export capability exists.

        Context keys: ``has_data_export`` (bool), ``export_formats`` (list[str]).
        """
        has_export = context.get("has_data_export", False)
        formats = context.get("export_formats", [])

        if has_export and len(formats) >= 1:
            return ComplianceStatus.COMPLIANT
        if has_export:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    async def _check_data_deletion_rights(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify data deletion capability exists (right to erasure).

        Context keys: ``has_data_deletion`` (bool), ``soft_delete`` (bool).
        """
        has_deletion = context.get("has_data_deletion", False)
        soft_delete = context.get("soft_delete", True)

        if has_deletion:
            if soft_delete:
                return ComplianceStatus.PARTIAL  # soft delete is acceptable but not ideal
            return ComplianceStatus.COMPLIANT
        return ComplianceStatus.NON_COMPLIANT

    async def _check_consent_management(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify consent tracking exists.

        Context keys: ``has_consent_tracking`` (bool), ``consent_version`` (str).
        """
        has_consent = context.get("has_consent_tracking", False)
        consent_version = context.get("consent_version", "")

        if has_consent and consent_version:
            return ComplianceStatus.COMPLIANT
        if has_consent:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    async def _check_audit_logging(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify audit logging is active and has sufficient coverage."""
        stats = self._audit_logger.get_statistics()
        total = stats.get("total", 0)
        if total > 10:
            return ComplianceStatus.COMPLIANT
        if total > 0:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    async def _check_access_review(self, context: dict[str, Any]) -> ComplianceStatus:
        """Verify access review cadence.

        Context keys: ``last_access_review_days`` (int — days since last review).
        """
        days_since_review = context.get("last_access_review_days")

        if days_since_review is None:
            return ComplianceStatus.UNKNOWN
        if days_since_review <= 90:
            return ComplianceStatus.COMPLIANT
        if days_since_review <= 180:
            return ComplianceStatus.PARTIAL
        return ComplianceStatus.NON_COMPLIANT

    def generate_report(self, report: ComplianceReport) -> dict[str, Any]:
        return {
            "id": report.id,
            "framework": report.framework.value,
            "generated_at": report.generated_at.isoformat(),
            "overall_status": report.overall_status.value,
            "summary": {
                "total_rules": report.total_rules,
                "compliant": report.compliant_rules,
                "non_compliant": report.non_compliant_rules,
                "compliance_rate": (report.compliant_rules / report.total_rules * 100) if report.total_rules > 0 else 0,
            },
            "results": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "status": r.status.value,
                    "details": r.details,
                }
                for r in report.results
            ],
        }


compliance_engine = ComplianceEngine()
