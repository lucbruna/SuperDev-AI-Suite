"""Prompt builder for agent system and task prompts."""

from __future__ import annotations

from typing import Any


class PromptBuilder:
    """Builds structured prompts for agents."""

    def __init__(self) -> None:
        self._sections: list[dict[str, str]] = []
        self._personality: list[str] = []
        self._constraints: list[str] = []
        self._examples: list[dict[str, str]] = []
        self._role: str = ""
        self._goal: str = ""

    def set_role(self, role: str) -> PromptBuilder:
        self._role = role
        return self

    def set_goal(self, goal: str) -> PromptBuilder:
        self._goal = goal
        return self

    def add_section(self, title: str, content: str) -> PromptBuilder:
        self._sections.append({"title": title, "content": content})
        return self

    def add_personality(self, trait: str) -> PromptBuilder:
        if trait not in self._personality:
            self._personality.append(trait)
        return self

    def add_constraint(self, constraint: str) -> PromptBuilder:
        if constraint not in self._constraints:
            self._constraints.append(constraint)
        return self

    def add_example(self, input_text: str, output_text: str) -> PromptBuilder:
        self._examples.append({"input": input_text, "output": output_text})
        return self

    def build_system_prompt(self) -> str:
        parts: list[str] = []
        if self._role:
            parts.append(f"# Role\nYou are {self._role}.")
        if self._goal:
            parts.append(f"# Goal\n{self._goal}")
        if self._personality:
            traits = ", ".join(self._personality)
            parts.append(f"# Personality\nYou are {traits}.")
        for section in self._sections:
            parts.append(f"# {section['title']}\n{section['content']}")
        if self._constraints:
            numbered = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(self._constraints))
            parts.append(f"# Constraints\n{numbered}")
        if self._examples:
            ex_parts: list[str] = ["# Examples"]
            for i, ex in enumerate(self._examples, 1):
                ex_parts.append(f"Example {i}:\nInput: {ex['input']}\nOutput: {ex['output']}")
            parts.append("\n".join(ex_parts))
        return "\n\n".join(parts)

    def build_task_prompt(self, task: str, context: dict[str, Any] | None = None) -> str:
        parts: list[str] = [f"# Task\n{task}"]
        if context:
            ctx_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
            parts.append(f"# Context\n{ctx_str}")
        parts.append("# Instructions\nComplete the task according to your role and constraints.")
        return "\n\n".join(parts)

    def build_context_prompt(self, context: dict[str, Any]) -> str:
        lines: list[str] = ["# Available Context"]
        for key, value in context.items():
            lines.append(f"- **{key}**: {value}")
        return "\n".join(lines)

    def reset(self) -> PromptBuilder:
        self._sections.clear()
        self._personality.clear()
        self._constraints.clear()
        self._examples.clear()
        self._role = ""
        self._goal = ""
        return self

    def snapshot(self) -> dict[str, Any]:
        return {
            "role": self._role,
            "goal": self._goal,
            "sections": len(self._sections),
            "personality": list(self._personality),
            "constraints": len(self._constraints),
            "examples": len(self._examples),
        }
