"""Prompt templates for intelligence LLM calls (kept small and stable)."""
from __future__ import annotations

SYSTEM_ARCHITECT = (
    "You are a senior software architect analyzing an architecture graph. "
    "Answer concisely and concretely, referencing actual nodes when possible."
)

Q_A_TEMPLATE = (
    "Given this architecture summary:\n"
    "{summary}\n\n"
    "Question: {question}\n\n"
    "Answer based only on the summary; say what you cannot infer."
)

EXECUTIVE_TEMPLATE = (
    "Given these findings: {findings}\n"
    "Write a short executive summary of the top priorities."
)


def qa_prompt(summary: str, question: str) -> str:
    return Q_A_TEMPLATE.format(summary=summary, question=question)


def executive_prompt(findings: list[str]) -> str:
    return EXECUTIVE_TEMPLATE.format(findings="; ".join(findings))
