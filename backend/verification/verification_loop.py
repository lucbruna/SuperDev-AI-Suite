from __future__ import annotations

from datetime import datetime

from ai_platform.providers.base_provider import BaseProvider
from ai_platform.providers.provider_registry import ProviderRegistry

from backend.verification.corrector import CodeCorrector
from backend.verification.executor import CodeExecutor
from backend.verification.generator import CodeGenerator
from backend.verification.models import (
    TestResult,
    VerificationResult,
    VerificationStage,
)
from backend.verification.reviewer import CodeReviewer
from backend.verification.tester import CodeTester


class VerificationLoop:
    def __init__(
        self,
        provider: BaseProvider | None = None,
        provider_name: str | None = None,
        max_iterations: int = 3,
    ):
        self.registry = ProviderRegistry()
        self.provider = provider or self._get_provider(provider_name)
        self.max_iterations = max_iterations
        
        self.generator = CodeGenerator(self.provider)
        self.executor = CodeExecutor()
        self.tester = CodeTester()
        self.reviewer = CodeReviewer(self.provider)
        self.corrector = CodeCorrector(self.provider)

    def _get_provider(self, provider_name: str | None) -> BaseProvider:
        if provider_name:
            provider_class = self.registry.get(provider_name)
            if provider_class:
                return provider_class()
        return self.registry.get("openai") or self.registry.get("anthropic") or self.registry.get("ollama")

    async def run(
        self,
        task_description: str,
        language: str = "python",
        context: str | None = None,
        requirements: list[str] | None = None,
        existing_code: str | None = None,
        test_files: dict[str, str] | None = None,
    ) -> VerificationResult:
        result = VerificationResult(
            task_description=task_description,
            language=language,
            max_iterations=self.max_iterations,
        )

        result.generation = await self.generator.generate(
            task_description=task_description,
            language=language,
            context=context,
            requirements=requirements,
            existing_code=existing_code,
        )

        if not result.generation.success:
            result.error = result.generation.error
            result.stage = VerificationStage.FAILED
            return result

        current_code = result.generation.code

        for iteration in range(self.max_iterations):
            result.iterations = iteration + 1
            
            execution = await self.executor.execute(current_code, language)
            result.execution = execution

            if not execution.success:
                correction = await self.corrector.correct(
                    code=current_code,
                    language=language,
                    test_result=TestResult(
                        success=False,
                        failures=[{"error": execution.stderr, "test": "execution"}],
                    ),
                    context=context,
                )
                if correction.success:
                    current_code = correction.corrected_code
                    result.correction = correction
                    continue
                else:
                    result.error = f"Execution failed: {execution.stderr}"
                    result.stage = VerificationStage.FAILED
                    return result

            test_result = await self.tester.run_tests(
                code=current_code,
                language=language,
                test_files=test_files,
            )
            result.testing = test_result

            if not test_result.success:
                correction = await self.corrector.correct(
                    code=current_code,
                    language=language,
                    test_result=test_result,
                    context=context,
                )
                if correction.success:
                    current_code = correction.corrected_code
                    result.correction = correction
                    continue
                else:
                    result.error = "Tests failed and could not be corrected"
                    result.stage = VerificationStage.FAILED
                    return result

            review_result = await self.reviewer.review(
                code=current_code,
                language=language,
                context=context,
            )
            result.review = review_result

            if review_result.score < 70 or review_result.security_issues:
                correction = await self.corrector.correct(
                    code=current_code,
                    language=language,
                    review_result=review_result,
                    context=context,
                )
                if correction.success:
                    current_code = correction.corrected_code
                    result.correction = correction
                    continue

            break

        result.final_code = current_code
        result.success = True
        result.stage = VerificationStage.COMPLETE
        result.completed_at = datetime.utcnow()

        return result

    async def run_with_callbacks(
        self,
        task_description: str,
        language: str = "python",
        context: str | None = None,
        requirements: list[str] | None = None,
        existing_code: str | None = None,
        test_files: dict[str, str] | None = None,
        on_stage_complete: callable | None = None,
    ) -> VerificationResult:
        result = VerificationResult(
            task_description=task_description,
            language=language,
            max_iterations=self.max_iterations,
        )

        result.generation = await self.generator.generate(
            task_description=task_description,
            language=language,
            context=context,
            requirements=requirements,
            existing_code=existing_code,
        )
        if on_stage_complete:
            await on_stage_complete(VerificationStage.GENERATE, result.generation)

        if not result.generation.success:
            result.error = result.generation.error
            result.stage = VerificationStage.FAILED
            return result

        current_code = result.generation.code

        for iteration in range(self.max_iterations):
            result.iterations = iteration + 1
            
            execution = await self.executor.execute(current_code, language)
            result.execution = execution
            if on_stage_complete:
                await on_stage_complete(VerificationStage.EXECUTE, execution)

            if not execution.success:
                correction = await self.corrector.correct(
                    code=current_code,
                    language=language,
                    test_result=TestResult(
                        success=False,
                        failures=[{"error": execution.stderr, "test": "execution"}],
                    ),
                    context=context,
                )
                if correction.success:
                    current_code = correction.corrected_code
                    result.correction = correction
                    if on_stage_complete:
                        await on_stage_complete(VerificationStage.CORRECT, correction)
                    continue
                else:
                    result.error = f"Execution failed: {execution.stderr}"
                    result.stage = VerificationStage.FAILED
                    return result

            test_result = await self.tester.run_tests(
                code=current_code,
                language=language,
                test_files=test_files,
            )
            result.testing = test_result
            if on_stage_complete:
                await on_stage_complete(VerificationStage.TEST, test_result)

            if not test_result.success:
                correction = await self.corrector.correct(
                    code=current_code,
                    language=language,
                    test_result=test_result,
                    context=context,
                )
                if correction.success:
                    current_code = correction.corrected_code
                    result.correction = correction
                    if on_stage_complete:
                        await on_stage_complete(VerificationStage.CORRECT, correction)
                    continue
                else:
                    result.error = "Tests failed and could not be corrected"
                    result.stage = VerificationStage.FAILED
                    return result

            review_result = await self.reviewer.review(
                code=current_code,
                language=language,
                context=context,
            )
            result.review = review_result
            if on_stage_complete:
                await on_stage_complete(VerificationStage.REVIEW, review_result)

            if review_result.score < 70 or review_result.security_issues:
                correction = await self.corrector.correct(
                    code=current_code,
                    language=language,
                    review_result=review_result,
                    context=context,
                )
                if correction.success:
                    current_code = correction.corrected_code
                    result.correction = correction
                    if on_stage_complete:
                        await on_stage_complete(VerificationStage.CORRECT, correction)
                    continue

            break

        result.final_code = current_code
        result.success = True
        result.stage = VerificationStage.COMPLETE
        result.completed_at = datetime.utcnow()

        if on_stage_complete:
            await on_stage_complete(VerificationStage.COMPLETE, result)

        return result