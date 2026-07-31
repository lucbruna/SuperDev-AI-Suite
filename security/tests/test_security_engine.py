"""Tests for the SecurityEngine orchestrator (Volume 16)."""

from __future__ import annotations

import pytest

from SuperDev.security.security_engine import SecurityEngine


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_start_stop(self) -> None:
        engine = SecurityEngine()
        assert not engine.is_running
        await engine.start()
        assert engine.is_running
        status = engine.status()
        assert len(status["subsystems"]) >= 15
        await engine.stop()
        assert not engine.is_running

    @pytest.mark.asyncio
    async def test_health(self, engine: SecurityEngine) -> None:
        health = await engine.health()
        assert health["running"] is True
        assert health["subsystems"] >= 15


class TestSubsystemWiring:
    def test_all_subsystems_exposed(self, engine: SecurityEngine) -> None:
        expected = {
            "owasp", "sbom", "secrets_detector", "vulnerability_engine",
            "dependency_scan", "encryption", "hashing", "signatures",
            "certificates", "vault", "secrets", "integrity", "compliance",
            "security_scan", "threat_detection",
        }
        assert expected.issubset(engine.subsystems().keys())

    def test_attribute_access(self, engine: SecurityEngine) -> None:
        assert engine.encryption is engine.subsystems()["encryption"]
        assert engine.vault is engine.subsystems()["vault"]

    def test_guard_access(self, engine: SecurityEngine) -> None:
        assert engine.guard is not None


class TestAggregateFlows:
    @pytest.mark.asyncio
    async def test_run_scan(self, engine: SecurityEngine) -> None:
        result = await engine.run_scan("demo")
        assert result["target"] == "demo"
        assert "scans" in result
        assert "total_findings" in result
        assert engine.metrics.get_counter("security.scans", {"target": "demo"}) >= 1

    def test_security_score_clean(self, engine: SecurityEngine) -> None:
        assert engine.security_score() == 1.0
