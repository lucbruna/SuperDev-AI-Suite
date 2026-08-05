"""Interview skill — question bank by phase for a guest conversation."""
from __future__ import annotations
from typing import Any

_PHASES = ["Warm-up", "Core", "Deep-dive", "Wrap-up"]
_TEMPLATES = [
    "How did you first get involved with {subject}?",
    "What is the most important lesson about {subject} you have learned?",
    "What is one thing about {subject} people usually get wrong?",
    "What is next for you and {subject}?",
]


class InterviewSkill:
    """Prepare a structured interview: warm-up, core, deep-dive and wrap-up."""

    skill_id = "interview"
    skill_name = "Interview"
    skill_version = "1.0.0"
    skill_description = "Interview question bank grouped by conversational phase."
    skill_category = "voice"
    skill_tags = ["voice", "interview", "questions", "script"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        guest: str,
        *,
        topic: str = "",
        question_count: int = 8,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a phase-grouped question bank, padded to the requested size."""
        subject = topic or guest
        questions: dict[str, list[str]] = {}
        for i, phase in enumerate(_PHASES):
            questions[phase] = [_TEMPLATES[i % len(_TEMPLATES)].format(subject=subject)]
        asked = sum(len(v) for v in questions.values())
        index = 0
        while asked < question_count:
            phase = _PHASES[index % len(_PHASES)]
            questions[phase].append(f"Tell us more about {subject} — follow-up {index + 1}.")
            asked += 1
            index += 1
        return {
            "platform": "interview",
            "guest": guest,
            "topic": topic,
            "language": language,
            "questions": questions,
            "question_count": asked,
        }
