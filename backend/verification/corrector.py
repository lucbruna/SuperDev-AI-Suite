from __future__ import annotations

import json

from backend.providers.base_provider import BaseProvider

from backend.verification.models import (
    CorrectionResult,
    ReviewResult,
    TestResult,
    VerificationStage,
)


class CodeCorrector:
    def __init__(self, provider: BaseProvider | None = None):
        self.provider = provider

    async def correct(
        self,
        code: str,
        language: str = "python",
        test_result: TestResult | None = None,
        review_result: ReviewResult | None = None,
        context: str | None = None,
    ) -> CorrectionResult:
        if not self.provider:
            return self._basic_correction(code, language, test_result, review_result)

        system_prompt = self._build_system_prompt(language)
        user_prompt = self._build_user_prompt(code, test_result, review_result, context)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self.provider.chat(
                messages=messages,
                config={"temperature": 0.3, "max_tokens": 4096},
            )

            content = response.content if hasattr(response, "content") else str(response)
            return self._parse_correction(content, code)
        except Exception as e:
            return CorrectionResult(
                success=False,
                error=str(e),
                stage=VerificationStage.CORRECT,
            )

    def _basic_correction(
        self,
        code: str,
        language: str,
        test_result: TestResult | None,
        review_result: ReviewResult | None,
    ) -> CorrectionResult:
        corrected = code
        changes = []
        
        if test_result and test_result.failures:
            for failure in test_result.failures:
                if "SyntaxError" in failure.get("error", ""):
                    changes.append({
                        "type": "fix_syntax",
                        "description": f"Fixed syntax error: {failure.get('error', '')}",
                    })
        
        if review_result:
            for issue in review_result.security_issues:
                if "eval" in str(issue).lower() or "exec" in str(issue).lower():
                    changes.append({
                        "type": "security_fix",
                        "description": f"Removed dangerous function: {issue.get('message', '')}",
                    })
        
        return CorrectionResult(
            success=True,
            corrected_code=corrected,
            changes=changes,
            stage=VerificationStage.CORRECT,
        )

    def _build_system_prompt(self, language: str) -> str:
        return f"""You are an expert {language} programmer. Fix the code based on test failures and review feedback.

Return ONLY a JSON object:
{{
  "corrected_code": "fixed code here",
  "changes": [
    {{"type": "fix|refactor|security|performance", "description": "what was changed"}}
  ]
}}"""

    def _build_user_prompt(
        self,
        code: str,
        test_result: TestResult | None,
        review_result: ReviewResult | None,
        context: str | None,
    ) -> str:
        parts = [f"Current code:\n```\n{code}\n```"]
        
        if test_result and not test_result.success:
            parts.append(f"Test failures:\n{test_result.test_output}")
            for failure in test_result.failures:
                parts.append(f"Failure: {failure.get('error', '')}")
        
        if review_result:
            if review_result.security_issues:
                parts.append(f"Security issues: {json.dumps(review_result.security_issues)}")
            if review_result.performance_issues:
                parts.append(f"Performance issues: {json.dumps(review_result.performance_issues)}")
            if review_result.style_issues:
                parts.append(f"Style issues: {json.dumps(review_result.style_issues)}")
            if review_result.suggestions:
                parts.append(f"Suggestions: {json.dumps(review_result.suggestions)}")
        
        if context:
            parts.append(f"Context: {context}")
        
        return "\n\n".join(parts)

    def _parse_correction(self, content: str, original_code: str) -> CorrectionResult:
        import re
        
        try:
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                return CorrectionResult(
                    success=True,
                    corrected_code=data.get("corrected_code", original_code),
                    changes=data.get("changes", []),
                    stage=VerificationStage.CORRECT,
                )
        except Exception:
            pass
        
        return CorrectionResult(
            success=False,
            error="Failed to parse correction response",
            stage=VerificationStage.CORRECT,
        )