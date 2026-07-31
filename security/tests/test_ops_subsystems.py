"""Tests for the vault, secrets, certificates, integrity, compliance, scan and threat subsystems."""

from __future__ import annotations

import pytest

from SuperDev.security.security_engine import SecurityEngine


class TestVault:
    def test_store_and_get(self, engine: SecurityEngine) -> None:
        engine.vault.store("db-pass", "valor", ttl_hours=1)
        assert engine.vault.get("db-pass") == "valor"
        assert engine.vault.list_names() == ["db-pass"]

    def test_versioning(self, engine: SecurityEngine) -> None:
        first = engine.vault.store("k", "v1")
        second = engine.vault.store("k", "v2")
        assert second.version == first.version + 1
        assert engine.vault.get("k") == "v2"

    def test_expiry(self, engine: SecurityEngine) -> None:
        engine.vault.store("temp", "v", ttl_hours=0)  # expires immediately
        assert engine.vault.get("temp") is None
        assert "temp" in engine.vault.expired()

    def test_delete(self, engine: SecurityEngine) -> None:
        engine.vault.store("x", "1")
        assert engine.vault.delete("x") is True
        assert engine.vault.delete("x") is False


class TestSecrets:
    def test_generate_password(self, engine: SecurityEngine) -> None:
        password = engine.secrets.generate_password(16)
        assert len(password) >= 16

    def test_validate_password(self, engine: SecurityEngine) -> None:
        result = engine.secrets.validate_password("Forte!123abc")
        assert result["valid"] is True
        assert result["entropy_bits"] > 40

    def test_weak_password(self, engine: SecurityEngine) -> None:
        result = engine.secrets.validate_password("abc")
        assert result["valid"] is False
        assert result["strength"] < 1.0

    def test_token(self, engine: SecurityEngine) -> None:
        token = engine.secrets.generate_api_key()
        assert engine.secrets.validate_token_format(token)


class TestCertificates:
    def test_issue_and_validate(self, engine: SecurityEngine) -> None:
        cert = engine.certificates.issue("api.superdev.app")
        assert engine.certificates.validate(cert.serial)["valid"] is True
        assert len(engine.certificates.list()) == 1

    def test_rotate(self, engine: SecurityEngine) -> None:
        cert = engine.certificates.issue("svc")
        rotated = engine.certificates.rotate(cert.serial)
        assert rotated is not None
        assert rotated.serial != cert.serial


class TestIntegrity:
    def test_register_and_verify(self, engine: SecurityEngine) -> None:
        data = b"artefato"
        report = engine.integrity.register_and_verify("artifact-1", data)
        assert report.status == "ok"
        tampered = engine.integrity.verify("artifact-1", data + b"!")
        assert tampered.status == "modified"
        assert tampered.changed_files == ["artifact-1"]

    def test_verify_without_baseline(self, engine: SecurityEngine) -> None:
        report = engine.integrity.verify("nada", b"data")
        assert report.status == "error"


class TestCompliance:
    def test_soc2_compliant(self, engine: SecurityEngine) -> None:
        result = engine.compliance.evaluate(
            "SOC2",
            {f"CC{i}": True for i in range(1, 10)},
        )
        assert result.status.value == "compliant"
        assert result.score == pytest.approx(1.0, abs=0.001)

    def test_gdpr_with_gaps(self, engine: SecurityEngine) -> None:
        result = engine.compliance.evaluate(
            "GDPR", {"ART5": True, "ART17": False}
        )
        assert result.status.value == "non_compliant"
        assert "ART17" in result.gaps

    def test_unsupported_standard(self, engine: SecurityEngine) -> None:
        result = engine.compliance.evaluate("ISO-99999")
        assert result.status.value == "not_applicable"


class TestSecurityScan:
    def test_aggregate_risk_score(self, engine: SecurityEngine) -> None:
        from SuperDev.security.base import SecurityFinding, SecurityReport, Severity

        reports = [
            SecurityReport(
                analyzer="t",
                findings=[
                    SecurityFinding(
                        rule_id="R1", title="x", description="", severity=Severity.CRITICAL
                    ),
                    SecurityFinding(
                        rule_id="R2", title="y", description="", severity=Severity.HIGH
                    ),
                ],
            ),
            SecurityReport(analyzer="u", findings=[]),
        ]
        result = engine.security_scan.aggregate("app", reports)
        assert result.total_findings == 2
        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.risk_score > 0
        assert engine.metrics.get_gauge("security.risk_score", {"target": "app"}) is not None

    def test_clean_scan_zero_risk(self, engine: SecurityEngine) -> None:
        result = engine.security_scan.aggregate("clean", [])
        assert result.total_findings == 0
        assert result.risk_score == 0.0


class TestThreatDetection:
    def test_brute_force(self, engine: SecurityEngine) -> None:
        engine.threat_detection._max_failed_logins = 3
        threats = []
        for _ in range(3):
            threats += engine.threat_detection.ingest(
                "login.failed", "gw", {"username": "admin"}
            )
        assert len(threats) == 1
        assert threats[0].severity.value == "high"

    def test_mitigate(self, engine: SecurityEngine) -> None:
        threats = engine.threat_detection.ingest(
            "vault.access", "gw", {"unauthorized": True}
        )
        assert len(threats) == 1
        threat_id = threats[0].threat_id
        assert engine.threat_detection.mitigate(threat_id) is True
        assert engine.threat_detection.list_threats()[0].mitigated is True

    def test_exfiltration(self, engine: SecurityEngine) -> None:
        threats = engine.threat_detection.ingest(
            "data.export", "worker", {"volume_mb": 500}
        )
        assert len(threats) == 1
        assert threats[0].severity.value == "high"
