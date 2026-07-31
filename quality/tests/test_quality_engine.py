from __future__ import annotations

import pytest

from SuperDev.quality.quality_engine import QualityEngine


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_start_stop(self) -> None:
        engine = QualityEngine()
        await engine.start()
        assert engine.is_running
        status = engine.status()
        assert len(status["subsystems"]) == 12
        assert all(s.get("initialized") for s in status["subsystems"].values())
        await engine.stop()
        assert not engine.is_running

    @pytest.mark.asyncio
    async def test_health(self, engine: QualityEngine) -> None:
        health = await engine.health()
        assert health["running"] is True
        assert health["subsystems_initialized"] == 12


class TestSubsystemWiring:
    def test_all_subsystems_exposed(self, engine: QualityEngine) -> None:
        assert engine.testing is not None
        assert engine.unit is not None
        assert engine.integration is not None
        assert engine.regression is not None
        assert engine.performance is not None
        assert engine.security_guard is not None
        assert engine.automation is not None
        assert engine.coverage is not None
        assert engine.analysis is not None
        assert engine.benchmarking is not None
        assert engine.reports is not None
        assert engine.validation is not None

    @pytest.mark.asyncio
    async def test_run_full_testing(self, engine: QualityEngine) -> None:
        output = await engine.run_full_testing("module_a", source="def f():\n    return 1\n")
        assert output["suite_id"]
        assert output["result"].status.value in ("passed", "failed")
        assert output["score"]["overall"] >= 0.0
        assert output["report_id"]


class TestQualityScore:
    def test_compute_score(self, engine: QualityEngine) -> None:
        result = engine.compute_score(
            "app", code=0.92, tests=0.95, security=0.98,
            performance=0.90, documentation=0.88,
        )
        # 0.92*0.25 + 0.95*0.25 + 0.98*0.2 + 0.9*0.15 + 0.88*0.15 ≈ 0.926
        assert result["overall"] == pytest.approx(0.926, abs=0.001)
        assert engine.metrics.get_gauge("quality.score", {"target": "app"}) == pytest.approx(0.926, abs=0.001)

    def test_score_registered(self, engine: QualityEngine) -> None:
        engine.compute_score("t", code=0.5, tests=0.5)
        assert len(engine.analysis.get_scores()) >= 1


class TestProductionGate:
    @pytest.mark.asyncio
    async def test_gate_approved(self, engine: QualityEngine) -> None:
        gate = await engine.evaluate_production_gate("app", {
            "quality_score": 0.95,
            "coverage": 0.85,
            "tests_passed": True,
            "blocked": False,
            "critical_findings": 0,
        })
        assert gate["decision"] == "approved"
        assert gate["blocked_reasons"] == []

    @pytest.mark.asyncio
    async def test_gate_blocked(self, engine: QualityEngine) -> None:
        gate = await engine.evaluate_production_gate("app", {
            "quality_score": 0.5,
            "coverage": 0.4,
            "tests_passed": False,
            "blocked": True,
            "critical_findings": 2,
        })
        assert gate["decision"] == "blocked"
        assert gate["blocked_reasons"]

    @pytest.mark.asyncio
    async def test_gate_metrics(self, engine: QualityEngine) -> None:
        await engine.evaluate_production_gate("app", {"quality_score": 0.9, "coverage": 0.8})
        assert engine.metrics.get_counter("quality.gates", {"decision": "approved"}) >= 1


class TestEvents:
    @pytest.mark.asyncio
    async def test_gate_event_emitted(self, engine: QualityEngine) -> None:
        received: list[dict] = []
        engine.event_bus.on("quality.gate.evaluated", lambda data: received.append(data))
        await engine.evaluate_production_gate("app", {"quality_score": 0.9, "coverage": 0.8})
        assert len(received) == 1
        assert received[0]["decision"] == "approved"
