from __future__ import annotations

import json

from backend.providers.base_provider import BaseProvider
from backend.verification.models import ReviewResult, VerificationStage


class CodeReviewer:
    def __init__(self, provider: BaseProvider | None = None):
        self.provider = provider

    async def review(
        self,
        code: str,
        language: str = "python",
        context: str | None = None,
    ) -> ReviewResult:
        if not self.provider:
            return self._basic_review(code, language)

        system_prompt = self._build_system_prompt(language)
        user_prompt = self._build_user_prompt(code, context)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self.provider.chat(
                messages=messages,
                config={"temperature": 0.2, "max_tokens": 4096},
            )

            content = response.content if hasattr(response, "content") else str(response)
            return self._parse_review(content)
        except Exception as e:
            return ReviewResult(
                success=False,
                error=str(e),
                stage=VerificationStage.REVIEW,
            )

    def _basic_review(self, code: str, language: str) -> ReviewResult:
        import re

        issues = []
        security_issues = []
        score = 100

        lines = code.split("\n")

        if language == "python":
            if "import *" in code:
                issues.append({"type": "style", "message": "Avoid wildcard imports", "severity": "warning"})
                score -= 5

            if re.search(r"except:\s*pass", code):
                issues.append({"type": "style", "message": "Bare except with pass", "severity": "warning"})
                score -= 10

            if "eval(" in code or "exec(" in code:
                security_issues.append(
                    {"type": "security", "message": "Use of eval/exec is dangerous", "severity": "critical"}
                )
                score -= 30

            if "os.system(" in code or "os.popen(" in code:
                security_issues.append(
                    {"type": "security", "message": "Use of os.system/os.popen is dangerous", "severity": "critical"}
                )
                score -= 30

            if "subprocess" in code and ("shell=True" in code or "call(" in code or "Popen(" in code):
                security_issues.append(
                    {
                        "type": "security",
                        "message": "subprocess with shell or direct call can be dangerous",
                        "severity": "high",
                    }
                )
                score -= 20

            if "__import__(" in code:
                security_issues.append(
                    {"type": "security", "message": "Dynamic imports with __import__ are risky", "severity": "high"}
                )
                score -= 15

            if len(lines) > 500:
                issues.append({"type": "style", "message": "File too long, consider splitting", "severity": "info"})
                score -= 5

        return ReviewResult(
            success=True,
            score=max(0, score),
            issues=issues,
            security_issues=security_issues,
            stage=VerificationStage.REVIEW,
        )

    def _build_system_prompt(self, language: str) -> str:
        return f"""You are an expert {language} code reviewer. Review code for:
1. Security vulnerabilities
2. Performance issues
3. Code quality and maintainability
4. Best practices
5. Bugs and edge cases

Output JSON format:
{{
  "score": 0-100,
  "security_issues": [{{"line": 1, "message": "...", "severity": "critical|high|medium|low"}}],
  "performance_issues": [{{"line": 1, "message": "...", "severity": "high|medium|low"}}],
  "style_issues": [{{"line": 1, "message": "...", "severity": "warning|info"}}],
  "suggestions": ["..."]
}}"""

    def _build_user_prompt(self, code: str, context: str | None) -> str:
        parts = [f"Code to review:\n```\n{code}\n```"]
        if context:
            parts.append(f"Context: {context}")
        return "\n\n".join(parts)

    def _parse_review(self, content: str) -> ReviewResult:
        try:
            import re

            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())

                return ReviewResult(
                    success=True,
                    score=data.get("score", 50),
                    security_issues=data.get("security_issues", []),
                    performance_issues=data.get("performance_issues", []),
                    style_issues=data.get("style_issues", []),
                    suggestions=data.get("suggestions", []),
                    stage=VerificationStage.REVIEW,
                )
        except Exception:
            pass

        return ReviewResult(
            success=False,
            error="Failed to parse review response",
            stage=VerificationStage.REVIEW,
        )
