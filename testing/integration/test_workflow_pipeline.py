"""Testes de integração: Pipeline completo Workflow → Runtime → Verificação."""

import pytest
from workflow_engine.core.engine import WorkflowEngine
from workflow_engine.graph.graph_builder import GraphBuilder
from runtime_engine.sandbox.sandbox import DefaultSandbox


class TestWorkflowPipeline:
    """Testes de integração para o pipeline completo de workflows."""

    @pytest.mark.asyncio
    async def test_workflow_grafo_execucao(self):
        """Testa que um grafo simples pode ser construído e validado."""
        builder = GraphBuilder()
        builder.add_node("start", {"type": "shell", "command": "echo inicio"})
        builder.add_node("process", {"type": "shell", "command": "echo processando"})
        builder.add_node("end", {"type": "shell", "command": "echo fim"})
        builder.add_edge("start", "process")
        builder.add_edge("process", "end")

        graph = builder.build()
        assert graph is not None
        assert not graph.has_cycle()

    @pytest.mark.asyncio
    async def test_sandbox_execucao_completa(self):
        """Testa execução completa no sandbox."""
        sandbox = DefaultSandbox()
        await sandbox.create()

        # Criar arquivo
        result = await sandbox.execute(["sh", "-c", "echo 'conteudo' > arquivo.txt"])
        assert result.exit_code == 0

        # Ler arquivo
        result = await sandbox.execute(["cat", "arquivo.txt"])
        assert result.exit_code == 0
        assert "conteudo" in result.stdout

        # Limpar
        await sandbox.destroy()

    @pytest.mark.asyncio
    async def test_sandbox_comandos_encadeados(self):
        """Testa encadeamento de comandos no sandbox."""
        sandbox = DefaultSandbox()
        await sandbox.create()

        # Criar diretório e arquivo
        result = await sandbox.execute([
            "sh", "-c", "mkdir -p dir && echo 'teste' > dir/arquivo.txt && cat dir/arquivo.txt"
        ])
        assert result.exit_code == 0
        assert "teste" in result.stdout

        await sandbox.destroy()

    @pytest.mark.asyncio
    async def test_sandbox_timeout(self):
        """Testa que timeout funciona corretamente."""
        from runtime_engine.sandbox.sandbox import SandboxPolicy

        sandbox = DefaultSandbox(SandboxPolicy(max_cpu_seconds=1))
        await sandbox.create()

        result = await sandbox.execute(["sleep", "10"], timeout=1)
        assert result.exit_code == -1
        assert "Timeout" in result.stderr

        await sandbox.destroy()
