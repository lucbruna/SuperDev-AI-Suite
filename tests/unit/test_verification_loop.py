import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.verification.verification_loop import VerificationLoop
from backend.verification.generator import CodeGenerator
from backend.verification.executor import CodeExecutor
from backend.verification.reviewer import CodeReviewer
from backend.verification.models import GenerationResult, ExecutionResult, ReviewResult, VerificationStage


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.chat.return_value = MagicMock(content='```python\nprint("hello")\n```')
    return provider


class TestCodeGenerator:
    @pytest.mark.asyncio
    async def test_gerar_codigo_basico(self, mock_provider):
        generator = CodeGenerator(mock_provider)
        result = await generator.generate("Criar uma função hello world em Python")
        assert result.code is not None
        assert len(result.code) > 0

    @pytest.mark.asyncio
    async def test_gerar_com_contexto(self, mock_provider):
        generator = CodeGenerator(mock_provider)
        result = await generator.generate(
            "Criar uma API REST",
            context="linguagem: python, framework: fastapi"
        )
        assert result.code is not None


class TestCodeExecutor:
    @pytest.mark.asyncio
    async def test_executar_python(self):
        executor = CodeExecutor()
        result = await executor.execute("print('olá mundo')", language="python")
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_executar_erro(self):
        executor = CodeExecutor()
        result = await executor.execute("1/0", language="python")
        assert result.exit_code != 0

    @pytest.mark.asyncio
    async def test_executar_timeout(self):
        executor = CodeExecutor()
        result = await executor.execute("import time; time.sleep(10)", language="python", timeout=1)
        assert result.exit_code == -1


class TestCodeReviewer:
    @pytest.mark.asyncio
    async def test_revisao_codigo_perigoso(self):
        reviewer = CodeReviewer()
        result = await reviewer.review(
            "import os\nos.system('rm -rf /')",
            language="python"
        )
        assert result.score < 70
        assert len(result.security_issues) > 0


class TestVerificationLoop:
    @pytest.mark.asyncio
    async def test_loop_completo(self, mock_provider):
        loop = VerificationLoop(provider=mock_provider, max_iterations=1)
        result = await loop.run(
            "Criar uma função que soma dois números",
            language="python"
        )
        assert result.stage in ("complete", "failed")
        assert result.iterations >= 1

    @pytest.mark.asyncio
    async def test_loop_com_callback(self, mock_provider):
        loop = VerificationLoop(provider=mock_provider, max_iterations=1)
        stages_seen = []

        def on_stage(stage, data):
            stages_seen.append(stage)

        result = await loop.run(
            "Criar hello world",
            language="python",
            on_stage_complete=on_stage,
        )
        assert len(stages_seen) > 0
