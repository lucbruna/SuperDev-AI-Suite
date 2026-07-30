from __future__ import annotations

from workflow.triggers.trigger_models import Trigger, TriggerStatus
from workflow.triggers.trigger_manager import TriggerManager
from workflow.triggers.trigger_evaluator import TriggerEvaluator


class TestTriggers:
    def test_trigger_defaults(self) -> None:
        t = Trigger(name="test")
        assert t.name == "test"
        assert t.status == TriggerStatus.INACTIVE

    def test_trigger_manager(self) -> None:
        mgr = TriggerManager()
        t = Trigger(name="test")
        mgr.register(t)
        assert t.status == TriggerStatus.ACTIVE
        assert mgr.get(t.id) == t

    def test_trigger_pause_resume(self) -> None:
        mgr = TriggerManager()
        t = Trigger(name="test")
        mgr.register(t)
        mgr.pause(t.id)
        assert t.status == TriggerStatus.INACTIVE
        mgr.resume(t.id)
        assert t.status == TriggerStatus.ACTIVE

    def test_trigger_evaluator(self) -> None:
        t = Trigger(name="test", config={"condition": {"value": True}})
        result = TriggerEvaluator.evaluate(t)
        assert result["matched"]
