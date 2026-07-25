"""Testes unitários para o Sandbox."""

import pytest
import asyncio
from runtime_engine.sandbox.sandbox import (
    DefaultSandbox,
    SandboxPolicy,
    create_sandbox,
)


class TestSandboxPolicy:
    """Testes para a política de sandbox."""

    def test_politica_padrao(self):
        policy = SandboxPolicy()
        assert policy.max_memory_mb == 512
        assert policy.max_cpu_seconds == 60
        assert policy.network_access is False

    def test_comandos_bloqueados(self):
        policy = SandboxPolicy()
        assert "rm -rf /" in policy.blocked_commands
        assert "shutdown" in policy.blocked_commands


class TestDefaultSandbox:
    """Testes para o DefaultSandbox."""

    @pytest.mark.asyncio
    async def test_criar_e_destruir(self):
        sandbox = DefaultSandbox()
        sandbox_id = await sandbox.create()
        assert sandbox_id is not None
        assert sandbox._work_dir is not None

        await sandbox.destroy()
        assert sandbox._work_dir is None

    @pytest.mark.asyncio
    async def test_executar_comando_simples(self):
        sandbox = DefaultSandbox()
        await sandbox.create()

        result = await sandbox.execute(["echo", "olá mundo"])
        assert result.exit_code == 0
        assert "olá mundo" in result.stdout

        await sandbox.destroy()

    @pytest.mark.asyncio
    async def test_executar_sem_criar(self):
        sandbox = DefaultSandbox()
        with pytest.raises(RuntimeError, match="not created"):
            await sandbox.execute(["echo", "test"])

    @pytest.mark.asyncio
    async def test_comando_bloqueado(self):
        sandbox = DefaultSandbox()
        await sandbox.create()

        result = await sandbox.execute(["rm", "-rf", "/"])
        assert result.exit_code == -1
        assert "Blocked" in result.stderr

        await sandbox.destroy()

    @pytest.mark.asyncio
    async def test_timeout(self):
        sandbox = DefaultSandbox(SandboxPolicy(max_cpu_seconds=1))
        await sandbox.create()

        result = await sandbox.execute(["sleep", "10"], timeout=1)
        assert result.exit_code == -1
        assert "Timeout" in result.stderr

        await sandbox.destroy()

    @pytest.mark.asyncio
    async def test_log_execucao(self):
        sandbox = DefaultSandbox()
        await sandbox.create()

        await sandbox.execute(["echo", "test"])
        assert len(sandbox.execution_log) == 1
        assert sandbox.execution_log[0]["exit_code"] == 0

        await sandbox.destroy()


class TestCreateSandbox:
    """Testes para a factory function."""

    def test_criar_sandbox_padrao(self):
        sandbox = create_sandbox(use_docker=False)
        assert isinstance(sandbox, DefaultSandbox)

    @pytest.mark.asyncio
    async def test_sandbox_padrao_funciona(self):
        sandbox = create_sandbox(use_docker=False)
        await sandbox.create()
        result = await sandbox.execute(["echo", "ok"])
        assert result.exit_code == 0
        await sandbox.destroy()
