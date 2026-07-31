from __future__ import annotations

from typing import Any


class SessionSummarizer:
    def __init__(self, llm_provider: str = "openai", model: str = "gpt-4o-mini"):
        self._provider = llm_provider
        self._model = model

    async def summarize_session(self, session_id: str, entries: list[dict[str, Any]]) -> str:
        if not entries:
            return "No activity to summarize."

        total = len(entries)
        goals = [e.get("goal", e.get("task", "")) for e in entries if e.get("goal") or e.get("task")]
        decisions = [e.get("decision", e.get("result", "")) for e in entries if e.get("decision") or e.get("result")]
        errors = [e.get("error", "") for e in entries if e.get("error")]

        summary_parts = [f"Session {session_id}: {total} entries."]
        if goals:
            summary_parts.append(f"Goals ({len(goals)}): {'; '.join(goals[:5])}")
        if decisions:
            summary_parts.append(f"Decisions ({len(decisions)}): {'; '.join(decisions[:5])}")
        if errors:
            summary_parts.append(f"Errors ({len(errors)}): {'; '.join(errors[:3])}")

        base_summary = "\n".join(summary_parts)

        if self._provider == "openai":
            return await self._llm_summarize(base_summary, entries)

        return base_summary

    async def _llm_summarize(self, base: str, entries: list[dict[str, Any]]) -> str:
        try:
            from openai import OpenAI

            client = OpenAI()
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the agent session concisely. Extract: key goals, decisions made, errors encountered, and outcomes.",
                    },
                    {"role": "user", "content": f"Session data:\n{base}\n\nEntries: {len(entries)}"},
                ],
                max_tokens=300,
                temperature=0.3,
            )
            return response.choices[0].message.content or base
        except ImportError:
            return base
        except Exception:
            return base

    async def summarize_key(self, key: str, values: list[Any]) -> str:
        if not values:
            return f"Key '{key}': no values."
        return f"Key '{key}': {len(values)} values stored."

    async def generate_title(self, session_id: str, entries: list[dict[str, Any]]) -> str:
        goals = [e.get("goal", e.get("task", "")) for e in entries if e.get("goal") or e.get("task")]
        if goals:
            return goals[0][:60]
        return f"Session {session_id[:8]}"
