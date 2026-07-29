import platform
import sys

import pytest
from runtime_engine.sandbox.sandbox import (
    DefaultSandbox,
    SandboxPolicy,
    create_sandbox,
)


class TestSandboxPolicy:
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
    @pytest.mark.asyncio
    async def test_criar_e_destruir(self):
        sandbox = DefaultSandbox()
        sandbox_id = await sandbox.create()
        assert sandbox_id is not None

        await sandbox.destroy()

    @pytest.mark.asyncio
    async def test_executar_comando_simples(self):
        sandbox = DefaultSandbox()
        await sandbox.create()

        cmd = ["echo", "ola mundo"]
        result = await sandbox.execute(cmd)
        assert result.exit_code == 0

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
