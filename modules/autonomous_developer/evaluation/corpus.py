"""Evaluation corpus — real bug fixtures for the fix-rate benchmark.

Each case is a self-contained repo (files dict) with a genuine bug, a goal,
and the plan a capable LLM would produce (the "oracle brain"). The harness
runs the full autonomous loop against the case with a mocked LLM and
measures whether the loop fixes the bug (tests pass) and what it cost.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["EvalCase", "CORPUS", "BUGGY_SUM", "FIXED_SUM", "TEST_SUM"]

BUGGY_SUM = '''"""Calculator: add returns the difference."""
def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a - b  # bug: subtracts instead of adding
'''

FIXED_SUM = '''"""Calculator: add returns the sum."""
def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
'''

TEST_SUM = '''"""Tests for the calculator."""
from calc import add


def test_add_positive():
    assert add(1, 2) == 3


def test_add_negative():
    assert add(-1, 1) == 0


def test_add_zero():
    assert add(0, 0) == 0
'''

BUGGY_UPPER = '''"""Text helper: upper returns lowercase."""
def upper(text: str) -> str:
    """Return the text uppercased."""
    return text.lower()  # bug: lowercases instead of uppercasing
'''

FIXED_UPPER = '''"""Text helper: upper returns uppercase."""
def upper(text: str) -> str:
    """Return the text uppercased."""
    return text.upper()
'''

TEST_UPPER = '''"""Tests for the text helper."""
from textutil import upper


def test_upper_plain():
    assert upper("abc") == "ABC"


def test_upper_mixed():
    assert upper("HeLLo") == "HELLO"


def test_upper_empty():
    assert upper("") == ""
'''

BUGGY_FIRST = '''"""List helper: first returns last."""
def first(items):
    """Return the first element of the list."""
    return items[-1]  # bug: returns the last element
'''

FIXED_FIRST = '''"""List helper: first returns first."""
def first(items):
    """Return the first element of the list."""
    return items[0]
'''

TEST_FIRST = '''"""Tests for the list helper."""
from lists import first


def test_first_nonempty():
    assert first([10, 20, 30]) == 10


def test_first_single():
    assert first([7]) == 7
'''


def _plan(goal: str, path: str, old_content: str, content: str) -> dict[str, Any]:
    return {
        "goal": goal,
        "tasks": [
            {
                "title": goal,
                "description": "Fix the wrong operator/logic so tests pass.",
                "priority": "high",
                "risk": "low",
                "files": [
                    {
                        "path": path,
                        "operation": "modify",
                        "old_content": old_content,
                        "content": content,
                        "reason": "Correct the faulty implementation.",
                    }
                ],
            }
        ],
    }


@dataclass(slots=True)
class EvalCase:
    """One benchmark case: a real bug + the plan that fixes it."""

    name: str
    goal: str
    files: dict[str, str]
    plan: dict[str, Any]
    work_branch: str = field(default="eval/fix")
    # When set, this case is expected to fail (plan does not fix the bug).
    expect_failure: bool = False


CORPUS: list[EvalCase] = [
    EvalCase(
        name="calc-add-subtract",
        goal="Fix add() so it returns the sum of its operands",
        files={"calc.py": BUGGY_SUM, "test_calc.py": TEST_SUM},
        plan=_plan(
            "Fix add() so it returns the sum of its operands",
            "calc.py",
            "    return a - b\n",
            FIXED_SUM,
        ),
    ),
    EvalCase(
        name="text-upper-lower",
        goal="Fix upper() so it returns the uppercase version of the text",
        files={"textutil.py": BUGGY_UPPER, "test_textutil.py": TEST_UPPER},
        plan=_plan(
            "Fix upper() so it returns the uppercase version of the text",
            "textutil.py",
            "    return text.lower()\n",
            FIXED_UPPER,
        ),
    ),
    EvalCase(
        name="list-first-last",
        goal="Fix first() so it returns the first element of the list",
        files={"lists.py": BUGGY_FIRST, "test_lists.py": TEST_FIRST},
        plan=_plan(
            "Fix first() so it returns the first element of the list",
            "lists.py",
            "    return items[-1]\n",
            FIXED_FIRST,
        ),
    ),
    EvalCase(
        name="calc-add-unfixed",
        goal="Fix add() so it returns the sum of its operands",
        files={"calc.py": BUGGY_SUM, "test_calc.py": TEST_SUM},
        plan=_plan(
            "Fix add() so it returns the sum of its operands",
            "calc.py",
            "    return a - b\n",
            BUGGY_SUM,  # does NOT fix the bug -> must fail at the test gate
        ),
        expect_failure=True,
    ),
]
