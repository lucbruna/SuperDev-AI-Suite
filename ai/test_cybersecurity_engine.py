"""Comprehensive tests for cybersecurity_engine (Volume 39)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from datetime import datetime, timedelta

from cybersecurity_engine import (
    ThreatSeverity, ThreatType, IncidentStatus, VulnerabilitySeverity,
    ComplianceStandard, AccessControl, Threat, Vulnerability, Incident,
    SecurityUser, AuditEntry, EncryptionKey, SecurityPolicy,
    CybersecurityEngine, SecurityManager,
)
from cybersecurity_engine.threat_detection import ThreatDetectionEngine
from cybersecurity_engine.threat_detection.threat_engine import DetectedThreat, ThreatCategory, ThreatSeverity as ThreatDetectionSeverity
from cybersecurity_engine.vulnerability import VulnerabilityEngine
from cybersecurity_engine.vulnerability.vulnerability_engine import VulnSeverity, VulnStatus
from cybersecurity_engine.identity import IdentityEngine
from cybersecurity_engine.identity.identity_engine import IdentityUser, AuthStatus, AccessLevel
from cybersecurity_engine.encryption import EncryptionEngine
from cybersecurity_engine.encryption.encryption_engine import Algorithm, KeyStatus
from cybersecurity_engine.monitoring import MonitoringEngine
from cybersecurity_engine.monitoring.monitoring_engine import AlertSeverity, AlertStatus, MonitoringRule
from cybersecurity_engine.incident_response import IncidentResponseEngine
from cybersecurity_engine.incident_response.incident_engine import IncidentPhase, IncidentSeverity, IncidentStatus as IRStatus
from cybersecurity_engine.compliance import ComplianceEngine
from cybersecurity_engine.compliance.compliance_engine import ComplianceFramework, ComplianceStatus
from cybersecurity_engine.penetration import PenetrationEngine
from cybersecurity_engine.penetration.pentest_engine import PentestPhase, VulnFinding as PentestVulnFinding
from cybersecurity_engine.audit import AuditEngine
from cybersecurity_engine.audit.audit_engine import AuditAction, AuditSeverity
from cybersecurity_engine.security_config import CybersecurityConfig
from cybersecurity_engine.security_factory import SecurityFactory
from cybersecurity_engine.security_registry import SecurityRegistry
from cybersecurity_engine.security_runtime import SecurityRuntime
from cybersecurity_engine.security_context import SecurityContext
from cybersecurity_engine.security_events import SecurityEvent, SecurityEventType
from cybersecurity_engine.security_metrics import SecurityMetrics
from cybersecurity_engine.security_logger import SecurityLogger


class TestCybersecurityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CybersecurityEngine()

    def test_report_threat(self):
        threat = Threat(threat_type=ThreatType.MALWARE, severity=ThreatSeverity.HIGH, source_ip="1.2.3.4", target="server1")
        result = self.engine.report_threat(threat)
        self.assertIsNotNone(self.engine.get_threat(result.threat_id))

    def test_get_threats_by_severity(self):
        t1 = Threat(severity=ThreatSeverity.LOW)
        t2 = Threat(severity=ThreatSeverity.CRITICAL)
        self.engine.report_threat(t1)
        self.engine.report_threat(t2)
        critical = self.engine.get_threats(ThreatSeverity.CRITICAL)
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0].severity, ThreatSeverity.CRITICAL)

    def test_add_vulnerability(self):
        vuln = Vulnerability(name="SQL Injection", severity=VulnerabilitySeverity.HIGH)
        self.engine.add_vulnerability(vuln)
        self.assertIsNotNone(self.engine.get_vulnerability(vuln.vuln_id))

    def test_create_incident(self):
        inc = Incident(title="Test incident", severity=ThreatSeverity.CRITICAL, assigned_to="admin")
        self.engine.create_incident(inc)
        self.assertIsNotNone(self.engine.get_incident(inc.incident_id))
        self.assertEqual(inc.assigned_to, "admin")

    def test_add_user(self):
        user = SecurityUser(username="alice", email="alice@test.com", role="admin")
        self.engine.add_user(user)
        self.assertIsNotNone(self.engine.get_user(user.user_id))

    def test_add_audit_entry(self):
        entry = AuditEntry(user_id="user1", action="login", resource="auth")
        self.engine.add_audit_entry(entry)
        log = self.engine.get_audit_log("user1")
        self.assertEqual(len(log), 1)

    def test_register_key(self):
        key = EncryptionKey(name="test-key", algorithm="AES-256")
        self.engine.register_key(key)
        self.assertIsNotNone(self.engine.get_key(key.key_id))
        self.assertTrue(key.is_active)

    def test_add_policy(self):
        policy = SecurityPolicy(name="data-retention", standard=ComplianceStandard.GDPR)
        self.engine.add_policy(policy)
        self.assertIsNotNone(self.engine.get_policy(policy.policy_id))

    def test_stats(self):
        stats = self.engine.get_stats()
        self.assertIn("threats", stats)


class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.config = CybersecurityConfig()
        self.manager = SecurityManager(self.config)

    def test_report_threat(self):
        result = self.manager.report_threat("phishing", "high", "1.2.3.4", "web-app", "Phishing attempt")
        self.assertIsNotNone(result)
        self.assertEqual(result.threat_type, ThreatType.PHISHING)

    def test_create_incident(self):
        inc = self.manager.create_incident("Test Incident", "high", ["server1", "server2"])
        self.assertIsNotNone(inc)
        self.assertEqual(inc.title, "Test Incident")

    def test_register_user(self):
        user = self.manager.register_user("admin", "admin@test.com", "admin")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")

    def test_authenticate_success(self):
        self.manager.register_user("alice", "alice@test.com", "admin")
        result = self.manager.authenticate("alice", "pass")
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result.username, "alice")

    def test_authenticate_failed(self):
        self.manager.register_user("alice", "alice@test.com", "admin")
        result = self.manager.authenticate("wrong_user", "pass")
        self.assertIsNone(result)

    def test_authorize(self):
        user = self.manager.register_user("admin_perm", "admin@test.com", "admin")
        self.assertTrue(self.manager.authorize(user.user_id, "resource", "read"))
        self.assertTrue(self.manager.authorize(user.user_id, "resource", "write"))

    def test_authorize_admin(self):
        user = self.manager.register_user("admin", "admin@test.com", "admin")
        self.assertTrue(self.manager.authorize(user.user_id, "resource", "write"))

    def test_scan_vulnerability(self):
        vuln = self.manager.scan_vulnerability("web-server", "high", 8.5)
        self.assertIsNotNone(vuln)
        self.assertEqual(vuln.severity, VulnerabilitySeverity.HIGH)

    def test_log_audit(self):
        entry = self.manager.log_audit("u1", "login", "auth", True)
        self.assertIsNotNone(entry)
        self.assertTrue(entry.success)

    def test_stats(self):
        stats = self.manager.get_stats()
        self.assertIn("threats", stats)


class TestThreatDetection(unittest.TestCase):
    def setUp(self):
        self.engine = ThreatDetectionEngine()

    def test_add_rule_and_analyze(self):
        self.engine.add_rule("brute_force", {"type": "brute_force", "count": 5})
        result = self.engine.analyze_event({"type": "brute_force", "count": 5, "source_ip": "1.2.3.4"})
        self.assertIsNotNone(result)
        self.assertEqual(result.severity, ThreatDetectionSeverity.MEDIUM)

    def test_no_match(self):
        self.engine.add_rule("malware", {"type": "malware"})
        result = self.engine.analyze_event({"type": "phishing"})
        self.assertIsNone(result)

    def test_block_ip(self):
        self.assertTrue(self.engine.block_ip("1.2.3.4"))
        self.assertTrue(self.engine.is_blocked("1.2.3.4"))
        self.assertFalse(self.engine.is_blocked("5.6.7.8"))

    def test_risk_score(self):
        threat = DetectedThreat(severity=ThreatDetectionSeverity.CRITICAL)
        score = self.engine.calculate_risk_score(threat)
        self.assertEqual(score, 1.0)

    def test_stats(self):
        self.engine.add_rule("test", {"type": "test"})
        stats = self.engine.get_stats()
        self.assertEqual(stats["rules"], 1)


class TestVulnerabilityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = VulnerabilityEngine()

    def test_scan_code(self):
        self.engine.add_rule("sql_injection", "SELECT *", severity="high")
        result = self.engine.scan_code("app", ["SELECT * FROM users", "print('hello')"])
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].severity, VulnSeverity.HIGH)

    def test_scan_dependencies(self):
        deps = [{"name": "requests", "version": "2.20", "vulnerabilities": [{"severity": "high", "description": "CVE-1234", "cvss": 8.5}]}]
        result = self.engine.scan_dependencies("app", deps)
        self.assertEqual(len(result.findings), 1)

    def test_update_status(self):
        self.engine.add_rule("sql_injection", "SELECT *", severity="high")
        scan = self.engine.scan_code("app", ["SELECT * FROM users"])
        finding_id = scan.findings[0].finding_id
        self.assertTrue(self.engine.update_status(finding_id, VulnStatus.REMEDIATED))
        self.assertEqual(self.engine.get_finding(finding_id).status, VulnStatus.REMEDIATED)

    def test_risk_score(self):
        self.engine.add_rule("sql_injection", "SELECT *", severity="high")
        self.engine.scan_code("app", ["SELECT * FROM users", "SELECT * FROM orders"])
        score = self.engine.get_risk_score()
        self.assertGreater(score, 0)

    def test_stats(self):
        self.engine.add_rule("sql_injection", "SELECT *", severity="high")
        self.engine.scan_code("app", ["SELECT * FROM users"])
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_findings"], 1)


class TestIdentityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = IdentityEngine(max_attempts=3, lockout_minutes=5)

    def test_create_user(self):
        user = IdentityUser(username="alice", email="alice@test.com", role="admin")
        self.engine.create_user(user)
        self.assertIsNotNone(self.engine.get_user(user.user_id))
        self.assertIsNotNone(self.engine.get_user_by_username("alice"))

    def test_authenticate_success(self):
        self.engine.create_user(IdentityUser(username="alice", role="admin"))
        result = self.engine.authenticate("alice", "pass", "1.2.3.4")
        self.assertEqual(result, AuthStatus.SUCCESS)

    def test_authenticate_failed(self):
        self.engine.create_user(IdentityUser(username="alice", role="admin"))
        result = self.engine.authenticate("wrong_user", "pass", "1.2.3.4")
        self.assertEqual(result, AuthStatus.FAILED)

    def test_lockout(self):
        self.engine.create_user(IdentityUser(username="alice", role="admin"))
        for _ in range(3):
            self.engine.authenticate("alice", "wrong", "1.2.3.4")
        result = self.engine.authenticate("alice", "pass", "1.2.3.4")
        self.assertEqual(result, AuthStatus.LOCKED)

    def test_unlock(self):
        user = IdentityUser(username="alice", role="admin")
        self.engine.create_user(user)
        self.engine.lock_user(user.user_id)
        self.assertTrue(self.engine.unlock_user(user.user_id))

    def test_authorize(self):
        user = IdentityUser(username="alice", role="admin")
        self.engine.create_user(user)
        self.assertTrue(self.engine.authorize(user.user_id, "resource", AccessLevel.ADMIN))

    def test_stats(self):
        self.engine.create_user(IdentityUser(username="alice"))
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_users"], 1)


class TestEncryptionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EncryptionEngine()

    def test_generate_key(self):
        key = self.engine.generate_key(Algorithm.AES256, 256)
        self.assertIsNotNone(key)
        self.assertEqual(key.status, KeyStatus.ACTIVE)

    def test_encrypt_decrypt(self):
        key = self.engine.generate_key()
        payload = self.engine.encrypt("secret data", key.key_id)
        self.assertIsNotNone(payload)
        result = self.engine.decrypt(payload.payload_id)
        self.assertIn("decrypted:", result)

    def test_rotate_key(self):
        old_key = self.engine.generate_key()
        new_key = self.engine.rotate_key(old_key.key_id)
        self.assertEqual(old_key.status, KeyStatus.EXPIRED)
        self.assertEqual(new_key.status, KeyStatus.ACTIVE)

    def test_revoke_key(self):
        key = self.engine.generate_key()
        self.assertTrue(self.engine.revoke_key(key.key_id))
        self.assertEqual(key.status, KeyStatus.REVOKED)

    def test_stats(self):
        self.engine.generate_key()
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_keys"], 1)


class TestMonitoringEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MonitoringEngine()

    def test_record_metric(self):
        snap = self.engine.record_metric("cpu_usage", 85.0, "%")
        self.assertEqual(snap.metric_name, "cpu_usage")
        self.assertEqual(snap.value, 85.0)

    def test_alert_generation(self):
        rule = MonitoringRule(name="high_cpu", metric="cpu_usage", threshold=80.0, operator="gt", severity=AlertSeverity.WARNING)
        self.engine.add_rule(rule)
        self.engine.record_metric("cpu_usage", 90.0, "%")
        alerts = self.engine.get_alerts(severity=AlertSeverity.WARNING)
        self.assertGreater(len(alerts), 0)

    def test_manual_alert(self):
        alert = self.engine.create_alert("Test alert", "Something happened", AlertSeverity.ERROR)
        self.assertIsNotNone(alert)

    def test_acknowledge_resolve(self):
        alert = self.engine.create_alert("Test alert")
        self.assertTrue(self.engine.acknowledge_alert(alert.alert_id))
        self.assertTrue(self.engine.resolve_alert(alert.alert_id))

    def test_stats(self):
        self.engine.record_metric("test", 1.0)
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_metrics"], 1)


class TestIncidentResponse(unittest.TestCase):
    def setUp(self):
        self.engine = IncidentResponseEngine()

    def test_create_incident(self):
        inc = self.engine.create_incident("Test", "Description", IncidentSeverity.HIGH, "alice")
        self.assertIsNotNone(inc)
        self.assertEqual(inc.assignee, "alice")

    def test_update_phase(self):
        inc = self.engine.create_incident("Test")
        self.assertTrue(self.engine.update_phase(inc.incident_id, IncidentPhase.ANALYSIS, "Analyzing"))
        self.assertEqual(inc.phase, IncidentPhase.ANALYSIS)
        self.assertGreater(len(inc.timeline), 0)

    def test_contain(self):
        inc = self.engine.create_incident("Test")
        self.assertTrue(self.engine.contain_incident(inc.incident_id, ["isolate network", "block ports"]))
        self.assertEqual(inc.status, IRStatus.CONTAINED)

    def test_resolve(self):
        inc = self.engine.create_incident("Test")
        self.assertTrue(self.engine.resolve_incident(inc.incident_id, "Fixed the issue"))
        self.assertEqual(inc.resolution, "Fixed the issue")

    def test_playbook(self):
        from cybersecurity_engine.incident_response.incident_engine import Playbook
        pb = Playbook(name="Malware Response", incident_type="malware", estimated_time_minutes=30)
        self.engine.add_playbook(pb)
        found = self.engine.get_playbook("malware")
        self.assertIsNotNone(found)

    def test_stats(self):
        self.engine.create_incident("Test")
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_incidents"], 1)


class TestComplianceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ComplianceEngine()

    def test_add_control(self):
        from cybersecurity_engine.compliance.compliance_engine import ComplianceControl
        ctrl = ComplianceControl(framework=ComplianceFramework.NIST, title="Access Control", status=ComplianceStatus.NOT_ASSESSED)
        self.engine.add_control(ctrl)
        self.assertIsNotNone(self.engine.get_control(ctrl.control_id))

    def test_update_control(self):
        from cybersecurity_engine.compliance.compliance_engine import ComplianceControl
        ctrl = ComplianceControl(framework=ComplianceFramework.GDPR, title="Data Protection")
        self.engine.add_control(ctrl)
        self.assertTrue(self.engine.update_control_status(ctrl.control_id, ComplianceStatus.COMPLIANT, ["Evidence 1"]))

    def test_assess_framework(self):
        from cybersecurity_engine.compliance.compliance_engine import ComplianceControl
        self.engine.add_control(ComplianceControl(framework=ComplianceFramework.SOC2, title="C1", status=ComplianceStatus.COMPLIANT))
        self.engine.add_control(ComplianceControl(framework=ComplianceFramework.SOC2, title="C2", status=ComplianceStatus.NON_COMPLIANT))
        assessment = self.engine.assess_framework(ComplianceFramework.SOC2)
        self.assertEqual(assessment.total_controls, 2)
        self.assertEqual(assessment.compliant, 1)

    def test_get_gaps(self):
        from cybersecurity_engine.compliance.compliance_engine import ComplianceControl
        self.engine.add_control(ComplianceControl(framework=ComplianceFramework.HIPAA, title="H1", status=ComplianceStatus.NON_COMPLIANT))
        gaps = self.engine.get_gaps(ComplianceFramework.HIPAA)
        self.assertEqual(len(gaps), 1)

    def test_stats(self):
        from cybersecurity_engine.compliance.compliance_engine import ComplianceControl
        self.engine.add_control(ComplianceControl(framework=ComplianceFramework.NIST, title="N1"))
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_controls"], 1)


class TestPenetrationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PenetrationEngine()

    def test_create_engagement(self):
        eng = self.engine.create_engagement("Test Pentest")
        self.assertIsNotNone(eng)
        self.assertEqual(eng.name, "Test Pentest")

    def test_add_target(self):
        from cybersecurity_engine.penetration.pentest_engine import PentestTarget
        eng = self.engine.create_engagement("Test")
        target = PentestTarget(hostname="web-server", ip_address="192.168.1.10", ports=[80, 443])
        self.assertTrue(self.engine.add_target(eng.engagement_id, target))

    def test_add_finding(self):
        from cybersecurity_engine.penetration.pentest_engine import PentestFinding
        eng = self.engine.create_engagement("Test")
        finding = PentestFinding(title="XSS", severity=PentestVulnFinding.HIGH, cvss=7.5)
        self.assertTrue(self.engine.add_finding(eng.engagement_id, finding))

    def test_update_phase(self):
        eng = self.engine.create_engagement("Test")
        self.assertTrue(self.engine.update_phase(eng.engagement_id, PentestPhase.EXPLOITATION))
        self.assertEqual(eng.phase, PentestPhase.EXPLOITATION)

    def test_generate_report(self):
        eng = self.engine.create_engagement("Test")
        report = self.engine.generate_report(eng.engagement_id)
        self.assertEqual(report["engagement"], "Test")

    def test_stats(self):
        self.engine.create_engagement("Test")
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_engagements"], 1)


class TestAuditEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AuditEngine(retention_days=90)

    def test_log(self):
        entry = self.engine.log(AuditAction.LOGIN, user_id="u1", resource="auth", ip_address="1.2.3.4")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action, AuditAction.LOGIN)

    def test_query(self):
        from cybersecurity_engine.audit.audit_engine import AuditQuery
        self.engine.log(AuditAction.CREATE, user_id="u1")
        self.engine.log(AuditAction.READ, user_id="u2")
        q = AuditQuery(user_id="u1")
        results = self.engine.query(q)
        self.assertEqual(len(results), 1)

    def test_get_user_history(self):
        self.engine.log(AuditAction.LOGIN, user_id="u1")
        self.engine.log(AuditAction.LOGOUT, user_id="u1")
        history = self.engine.get_user_history("u1")
        self.assertEqual(len(history), 2)

    def test_get_failed_actions(self):
        self.engine.log(AuditAction.LOGIN, success=False)
        self.engine.log(AuditAction.LOGIN, success=True)
        failed = self.engine.get_failed_actions()
        self.assertEqual(len(failed), 1)

    def test_stats(self):
        self.engine.log(AuditAction.READ)
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_entries"], 1)


class TestInfrastructure(unittest.TestCase):
    def test_config(self):
        config = CybersecurityConfig()
        self.assertIsNotNone(config)

    def test_factory(self):
        threat = SecurityFactory.create_threat("malware", "high", "1.2.3.4", "server1")
        self.assertIsNotNone(threat)
        vuln = SecurityFactory.create_vulnerability("SQLi", "db", "high", 8.0)
        self.assertIsNotNone(vuln)
        incident = SecurityFactory.create_incident("Breach", "critical", ["server1"])
        self.assertIsNotNone(incident)
        user = SecurityFactory.create_user("admin", "admin@test.com", "admin")
        self.assertIsNotNone(user)
        key = SecurityFactory.create_key("master", "AES-256", "encryption")
        self.assertIsNotNone(key)
        policy = SecurityFactory.create_policy("retention", "gdpr")
        self.assertIsNotNone(policy)
        entry = SecurityFactory.create_audit_entry("u1", "login", "auth")
        self.assertIsNotNone(entry)

    def test_registry(self):
        reg = SecurityRegistry()
        self.assertIsNotNone(reg)

    def test_runtime(self):
        rt = SecurityRuntime()
        self.assertIsNotNone(rt)

    def test_context(self):
        ctx = SecurityContext()
        self.assertIsNotNone(ctx)

    def test_event_bus(self):
        event = SecurityEvent(event_type=SecurityEventType.THREAT_DETECTED, source="test")
        self.assertIsNotNone(event)

    def test_metrics(self):
        m = SecurityMetrics()
        m.record_threat()
        m.record_vulnerability()
        self.assertIsNotNone(m)

    def test_logger(self):
        l = SecurityLogger()
        self.assertIsNotNone(l)


if __name__ == "__main__":
    unittest.main(verbosity=2)
