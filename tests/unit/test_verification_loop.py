"""Testes unitários para o VerificationLoop."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.verification.verification_loop import (
    VerificationLoop,
    CodeGenerator,
    CodeExecutor,
    CodeTester,
    CodeReviewer,
    CodeCorrector,
)


class TestCodeGenerator:
    """Testes para o CodeGenerator."""

    @pytest.mark.asyncio
    async def test_gerar_codigo_basico(self):
        generator = CodeGenerator()
        result = await generator.generate("Criar uma função hello world em Python")
        assert result.code is not None
        assert len(result.code) > 0

    @pytest.mark.asyncio
    async def test_gerar_com_contexto(self):
        generator = CodeGenerator()
        result = await generator.generate(
            "Criar uma API REST",
            context={"linguagem": "python", "framework": "fastapi"}
        )
        assert result.code is not None


class TestCodeExecutor:
    """Testes para o CodeExecutor."""

    @pytest.mark.asyncio
    async def test_executar_python(self):
        executor = CodeExecutor()
        result = await executor.execute("print('olá mundo')", language="python")
        assert result.exit_code == 0
        assert "olá mundo" in result.stdout

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
    """Testes para o CodeReviewer."""

    @pytest.mark.asyncio
    async def test_revisao_basica(self):
        reviewer = CodeReviewer()
        result = await reviewer.review("print('olá')", language="python")
        assert result.score >= 0
        assert result.score <= 100

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
    """Testes para o VerificationLoop."""

    @pytest.mark.asyncio
    async def test_loop_completo(self):
        loop = VerificationLoop(max_iterations=3)
        result = await loop.run(
        "Criar uma função que soma dois números",
            language="python"
        )
        assert result.stage in ("complete", "failed")
        assert result.iterations >= 1

    @pytest.mark.asyncio
    async def test_loop_com_callback(self):
        loop = VerificationLoop(max_iterations=2)
        stages_seen = []

        def on_stage(stage, data):
            stages_seen.append(stage)

        result = await loop.run(
            "Criar hello world",
            language="python",
            on_stage_complete=on_stage,
        )
        assert len(stages_seen) > 0
