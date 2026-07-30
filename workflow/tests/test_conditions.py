from __future__ import annotations

from workflow.conditions.condition_models import Condition, ConditionOperator
from workflow.conditions.condition_evaluator import ConditionEvaluator
from workflow.conditions.condition_composite import ConditionComposite
from workflow.conditions.condition_parser import ConditionParser
from workflow.conditions.condition_context import ConditionContext


class TestConditions:
    def test_condition_equals(self) -> None:
        c = Condition(field="status", operator=ConditionOperator.EQUALS, value="ok")
        assert ConditionEvaluator.evaluate(c, {"status": "ok"})
        assert not ConditionEvaluator.evaluate(c, {"status": "fail"})

    def test_condition_greater_than(self) -> None:
        c = Condition(field="count", operator=ConditionOperator.GREATER_THAN, value=5)
        assert ConditionEvaluator.evaluate(c, {"count": 10})
        assert not ConditionEvaluator.evaluate(c, {"count": 3})

    def test_condition_exists(self) -> None:
        c = Condition(field="name", operator=ConditionOperator.EXISTS)
        assert ConditionEvaluator.evaluate(c, {"name": "test"})
        assert not ConditionEvaluator.evaluate(c, {})

    def test_condition_composite_all(self) -> None:
        c1 = Condition(field="a", operator=ConditionOperator.EQUALS, value=1)
        c2 = Condition(field="b", operator=ConditionOperator.EQUALS, value=2)
        assert ConditionComposite.all([c1, c2], {"a": 1, "b": 2})
        assert not ConditionComposite.all([c1, c2], {"a": 1, "b": 3})

    def test_condition_composite_any(self) -> None:
        c1 = Condition(field="a", operator=ConditionOperator.EQUALS, value=1)
        c2 = Condition(field="b", operator=ConditionOperator.EQUALS, value=2)
        assert ConditionComposite.any([c1, c2], {"a": 1, "b": 3})
        assert not ConditionComposite.any([c1, c2], {"a": 0, "b": 3})

    def test_condition_parser(self) -> None:
        c = ConditionParser.parse({"field": "x", "operator": "equals", "value": 1})
        assert c.field == "x"
        assert c.operator == ConditionOperator.EQUALS
        assert c.value == 1

    def test_condition_context(self) -> None:
        ctx = ConditionContext({"key": "val"})
        assert ctx.get("key") == "val"
        assert "key" in ctx
        assert "missing" not in ctx
