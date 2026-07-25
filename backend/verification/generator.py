from __future__ import annotations

import json
from typing import Any

from ai_platform.providers.base_provider import BaseProvider, ChatResponse, Message
from backend.verification.models import GenerationResult, VerificationStage


class CodeGenerator:
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    async def generate(
        self,
        task_description: str,
        language: str = "python",
        context: str | None = None,
        requirements: list[str] | None = None,
        existing_code: str | None = None,
    ) -> GenerationResult:
        system_prompt = self._build_system_prompt(language, requirements)
        user_prompt = self._build_user_prompt(task_description, context, existing_code)

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]

        try:
            response = await self.provider.chat(
                messages=messages,
                config={"temperature": 0.3, "max_tokens": 4096},
            )

            content = response.content if hasattr(response, "content") else str(response)
            code = self._extract_code(content, language)

            return GenerationResult(
                success=True,
                code=code,
                language=language,
                metadata={"raw_response": content},
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
                language=language,
            )

    def _build_system_prompt(self, language: str, requirements: list[str] | None) -> str:
        req_text = "\n".join(f"- {r}" for r in (requirements or []))
        return f"""You are an expert {language} programmer. Generate clean, production-ready code.

Requirements:
{req_text if req_text else "- Write clean, well-documented code"}

Output format:
```{language}
// Your code here
```

Only output the code block, no additional explanation."""

    def _build_user_prompt(
        self,
        task_description: str,
        context: str | None,
        existing_code: str | None,
    ) -> str:
        parts = [f"Task: {task_description}"]

        if context:
            parts.append(f"Context:\n{context}")

        if existing_code:
            parts.append(f"Existing code to modify:\n```\n{existing_code}\n```")

        return "\n\n".join(parts)

    def _extract_code(self, content: str, language: str) -> str:
        import re

        pattern = rf"```{language}\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()

        pattern = r"```\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            return matches[0].strip()

        return content.strip()