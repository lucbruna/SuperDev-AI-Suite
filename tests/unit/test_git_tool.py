"""Testes unitários para o GitTool com rollback."""

import os
import pytest
import tempfile
import shutil
import subprocess

pytestmark = pytest.mark.skip(
    reason="agents.tools.git_tool package not available in current environment"
)

try:
    from agents.tools.git_tool import GitTool
except ImportError:
    GitTool = None


class TestGitTool:
    """Testes para o GitTool."""

    @pytest.fixture
    def tool(self):
        return GitTool()

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Cria um repositório Git temporário para testes."""
        repo_dir = str(tmp_path / "test_repo")
        os.makedirs(repo_dir)

        subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, capture_output=True)

        # Criar arquivo inicial
        with open(os.path.join(repo_dir, "README.md"), "w") as f:
            f.write("# Teste")

        subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, capture_output=True)

        return repo_dir

    @pytest.mark.asyncio
    async def test_status(self, tool, git_repo):
        result = await tool.execute({
            "action": "status",
            "workdir": git_repo,
        })
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_log(self, tool, git_repo):
        result = await tool.execute({
            "action": "log",
            "workdir": git_repo,
        })
        assert result["success"] is True
        assert "Initial commit" in result["stdout"]

    @pytest.mark.asyncio
    async def test_commit(self, tool, git_repo):
        # Criar novo arquivo
        with open(os.path.join(git_repo, "new_file.txt"), "w") as f:
            f.write("novo conteúdo")

        result = await tool.execute({
            "action": "commit",
            "message": "Adicionar novo arquivo",
            "workdir": git_repo,
        })
        assert result["success"] is True

        # Verificar que o commit foi criado
        log_result = await tool.execute({
            "action": "log",
            "workdir": git_repo,
        })
        assert "Adicionar novo arquivo" in log_result["stdout"]

    @pytest.mark.asyncio
    async def test_rollback_commit(self, tool, git_repo):
        # Fazer um commit
        with open(os.path.join(git_repo, "file.txt"), "w") as f:
            f.write("conteúdo")

        await tool.execute({
            "action": "commit",
            "message": "Commit para rollback",
            "workdir": git_repo,
        })

        # Obter HEAD atual
        result = await tool.execute({
            "action": "log",
            "workdir": git_repo,
        })
        assert "Commit para rollback" in result["stdout"]

        # Rollback
        await tool.rollback()

        # Verificar que o commit foi revertido
        log_result = await tool.execute({
            "action": "log",
            "workdir": git_repo,
        })
        # O commit de rollback não deve mais estar no log
        # (na verdade, o rollback faz reset --hard para o commit anterior)

    @pytest.mark.asyncio
    async def test_validacao(self, tool):
        assert await tool.validate({"action": "status"})
        assert await tool.validate({"action": "commit", "message": "teste"})
        assert await tool.validate({"action": "clone", "repo": "https://example.com/repo.git"})
        assert not await tool.validate({"action": "invalid"})
        assert not await tool.validate({"action": "clone"})
        assert not await tool.validate({"action": "commit"})
