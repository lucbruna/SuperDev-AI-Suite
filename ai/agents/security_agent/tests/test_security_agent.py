from __future__ import annotations

from ..audit import Audit
from ..authentication_review import AuthenticationReview
from ..authorization_review import AuthorizationReview
from ..dependency_scanner import DependencyScanner
from ..encryption_review import EncryptionReview
from ..owasp_analyzer import OWASPAnalyzer
from ..permissions_analyzer import PermissionsAnalyzer
from ..secrets_detector import SecretsDetector
from ..security_agent import SecurityAgent
from ..vulnerability_report import VulnerabilityReport


class TestOWASPAnalyzer:
    def test_analyze_code_sql(self) -> None:
        oa = OWASPAnalyzer()
        results = oa.analyze_code("execute('SELECT * FROM users')")
        assert any(r["id"] == "sql_injection" for r in results)

    def test_add_finding(self) -> None:
        oa = OWASPAnalyzer()
        oa.add_finding("custom", "Custom Vuln", "high", "test")
        assert oa.finding_count > 0

    def test_list_findings(self) -> None:
        oa = OWASPAnalyzer()
        oa.add_finding("f1", "Test", "low", "desc")
        assert len(oa.list_findings()) >= 1

    def test_owasp_top_10(self) -> None:
        oa = OWASPAnalyzer()
        assert len(oa.owasp_top_10) == 10

    def test_to_dict(self) -> None:
        oa = OWASPAnalyzer()
        d = oa.to_dict()
        assert "findings" in d


class TestDependencyScanner:
    def test_add_dependency(self) -> None:
        ds = DependencyScanner()
        ds.add_dependency("lodash", "4.17.21")
        assert ds.dependency_count == 1

    def test_scan_vulnerabilities(self) -> None:
        ds = DependencyScanner()
        ds.add_dependency("safe", "1.0.0")
        ds.add_dependency("unsafe", "0.0.1", ["CVE-2024-0001"])
        assert len(ds.scan_vulnerabilities()) == 1

    def test_vulnerable_count(self) -> None:
        ds = DependencyScanner()
        ds.add_dependency("bad", "1.0", ["CVE-1"])
        assert ds.vulnerable_count == 1

    def test_to_dict(self) -> None:
        ds = DependencyScanner()
        ds.add_dependency("pkg", "1.0")
        assert "dependencies" in ds.to_dict()


class TestSecretsDetector:
    def test_scan_text_api_key(self) -> None:
        sd = SecretsDetector()
        results = sd.scan_text("api_key = 'sk-test1234567890123456'")
        assert len(results) > 0

    def test_add_pattern(self) -> None:
        sd = SecretsDetector()
        sd.add_pattern("my_pattern", r"test_pattern", "low")
        assert sd.pattern_count > 0

    def test_scan_file(self) -> None:
        sd = SecretsDetector()
        results = sd.scan_file("/path/to/file")
        assert isinstance(results, list)

    def test_to_dict(self) -> None:
        sd = SecretsDetector()
        d = sd.to_dict()
        assert "patterns" in d


class TestPermissionsAnalyzer:
    def test_add_role(self) -> None:
        pa = PermissionsAnalyzer()
        pa.add_role("admin", ["read", "write"])
        assert pa.role_count == 1

    def test_check_access(self) -> None:
        pa = PermissionsAnalyzer()
        pa.add_role("user", ["read"])
        assert pa.check_access("user", "read") is True
        assert pa.check_access("user", "write") is False

    def test_analyze_least_privilege(self) -> None:
        pa = PermissionsAnalyzer()
        suggestions = pa.analyze_least_privilege(["admin", "read"])
        assert len(suggestions) > 0

    def test_to_dict(self) -> None:
        pa = PermissionsAnalyzer()
        pa.add_role("r", ["p"])
        assert "roles" in pa.to_dict()


class TestVulnerabilityReport:
    def test_add_vulnerability(self) -> None:
        vr = VulnerabilityReport()
        vr.add_vulnerability("CVE-1", "critical", "RCE", "patch")
        assert vr.total_count == 1

    def test_list_by_severity(self) -> None:
        vr = VulnerabilityReport()
        vr.add_vulnerability("v1", "critical", "desc")
        vr.add_vulnerability("v2", "low", "desc")
        assert len(vr.list_vulnerabilities("critical")) == 1

    def test_count_properties(self) -> None:
        vr = VulnerabilityReport()
        vr.add_vulnerability("v1", "critical", "desc")
        assert vr.critical_count == 1
        assert vr.high_count == 0

    def test_generate_report(self) -> None:
        vr = VulnerabilityReport()
        vr.add_vulnerability("v1", "high", "desc", "fix it")
        report = vr.generate_report()
        assert "Vulnerability Report" in report

    def test_to_dict(self) -> None:
        vr = VulnerabilityReport()
        vr.add_vulnerability("v", "low", "d")
        d = vr.to_dict()
        assert "vulnerabilities" in d


class TestAuthenticationReview:
    def test_review_config(self) -> None:
        ar = AuthenticationReview()
        results = ar.review_config({"password_min_length": True})
        assert len(results) == 6

    def test_grade(self) -> None:
        ar = AuthenticationReview()
        ar.review_config({})
        grade = ar.grade()
        assert grade in ("A", "B", "C", "D", "F")

    def test_to_dict(self) -> None:
        ar = AuthenticationReview()
        ar.review_config({})
        d = ar.to_dict()
        assert "findings" in d


class TestAuthorizationReview:
    def test_add_policy(self) -> None:
        ar = AuthorizationReview()
        ar.add_policy("p1", "allow", "read", "docs")
        assert ar.policy_count == 1

    def test_evaluate_access(self) -> None:
        ar = AuthorizationReview()
        ar.add_policy("p1", "allow", "read", "docs")
        result = ar.evaluate_access("user", "read", "docs")
        assert result["allowed"] is True

    def test_review_policy(self) -> None:
        ar = AuthorizationReview()
        findings = ar.review_policy({"effect": "allow", "resource": "*"})
        assert len(findings) > 0

    def test_to_dict(self) -> None:
        ar = AuthorizationReview()
        ar.add_policy("p", "allow", "a", "r")
        assert "policies" in ar.to_dict()


class TestEncryptionReview:
    def test_review_weak_algorithm(self) -> None:
        er = EncryptionReview()
        result = er.review_algorithm("MD5", 128)
        assert result["status"] == "non-compliant"

    def test_review_strong_algorithm(self) -> None:
        er = EncryptionReview()
        result = er.review_algorithm("AES-256", 256)
        assert result["status"] == "compliant"

    def test_add_standard(self) -> None:
        er = EncryptionReview()
        er.add_standard("SOC2", "AES-256", 256)
        assert er.standard_count == 1

    def test_to_dict(self) -> None:
        er = EncryptionReview()
        er.add_standard("s", "AES", 128)
        assert "standards" in er.to_dict()


class TestAudit:
    def test_log_event(self) -> None:
        a = Audit()
        eid = a.log_event("login", "user1", "system", "success")
        assert eid.startswith("evt_")

    def test_list_events(self) -> None:
        a = Audit()
        a.log_event("login", "u1", "sys", "ok")
        assert len(a.list_events()) == 1

    def test_search(self) -> None:
        a = Audit()
        a.log_event("login", "admin", "server", "ok")
        results = a.search("admin")
        assert len(results) == 1

    def test_generate_report(self) -> None:
        a = Audit()
        a.log_event("login", "u", "s", "ok")
        report = a.generate_audit_report()
        assert "Audit Report" in report

    def test_to_dict(self) -> None:
        a = Audit()
        a.log_event("t", "a", "r", "ok")
        d = a.to_dict()
        assert "events" in d


class TestSecurityAgent:
    def test_engine_initializes(self) -> None:
        sa = SecurityAgent()
        assert sa.owasp is not None
        assert sa.dependency_scanner is not None
        assert sa.secrets_detector is not None
        assert sa.permissions is not None
        assert sa.vulnerability_report is not None
        assert sa.auth_review is not None
        assert sa.authz_review is not None
        assert sa.encryption is not None
        assert sa.audit is not None

    def test_run_security_audit(self) -> None:
        sa = SecurityAgent()
        result = sa.run_security_audit({"code": "test"})
        assert result["status"] == "completed"

    def test_get_status(self) -> None:
        sa = SecurityAgent()
        s = sa.get_status()
        assert "owasp_findings" in s

    def test_to_dict(self) -> None:
        sa = SecurityAgent()
        d = sa.to_dict()
        assert d["agent"] == "security_agent"
