"""Tests for the QualityEngine production gate integration in the DevOps flow."""

from __future__ import annotations

import pytest

from devops.deployment import DevOpsQualityGate
from devops.devops_engine import DevOpsEngine


class TestQualityGate:
    def test_blocks_low_quality(self) -> None:
        gate = DevOpsQualityGate()
        result = gate.guard_deploy(
            "api",
            {
                "quality_score": 0.5,
                "coverage": 0.3,
                "tests_passed": False,
                "critical_findings": 2,
            },
        )
        assert result["decision"] == "blocked"
        assert result["blocked_reasons"]

    def test_approves_high_quality(self) -> None:
        gate = DevOpsQualityGate()
        result = gate.guard_deploy(
            "api",
            {
                "quality_score": 0.95,
                "coverage": 0.9,
                "tests_passed": True,
                "critical_findings": 0,
            },
        )
        assert result["decision"] == "approved"
        assert result["quality_score"] == pytest.approx(0.95, abs=0.001)

    def test_gate_can_be_reused(self) -> None:
        gate = DevOpsQualityGate()
        first = gate.guard_deploy("api", {"quality_score": 0.5})
        second = gate.guard_deploy("api", {"quality_score": 0.99, "coverage": 0.99})
        assert first["decision"] == "blocked"
        assert second["decision"] == "approved"


class TestDevOpsEngineWiring:
    def test_deploy_with_quality_blocks(self) -> None:
        engine = DevOpsEngine()
        result = engine.deploy_with_quality(
            "api",
            "production",
            signals={"quality_score": 0.4, "coverage": 0.2},
        )
        assert result["status"] == "blocked"
        assert result["deployed"] is False
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.deploys_blocked") >= 1

    def test_deploy_with_quality_approves(self) -> None:
        engine = DevOpsEngine()
        result = engine.deploy_with_quality(
            "api",
            "staging",
            signals={"quality_score": 0.9, "coverage": 0.9, "tests_passed": True},
        )
        assert result["status"] == "healthy"
        assert result["deployed"] is True
        assert result["deployment_id"] is not None
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.deploys") >= 1

    def test_quality_gate_exposed_on_engine(self) -> None:
        engine = DevOpsEngine()
        assert engine.quality_gate is not None
        assert engine.quality_gate.status()["available"] is False  # lazy — ainda não usado
