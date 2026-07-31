from __future__ import annotations

from frontend import FrontendEngine


def test_engine_initialize_and_status() -> None:
    engine = FrontendEngine()
    assert engine.status()["initialized"] is False
    engine.initialize()
    status = engine.status()
    assert status["initialized"] is True
    assert status["platform"] == "web"


def test_engine_runs_directly() -> None:
    engine = FrontendEngine()
    engine.initialize()
    assert engine is not None
