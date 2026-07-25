"""Testes unitários para o FilesystemTool com rollback."""

import os
import pytest
import tempfile
import shutil
from agents.tools.filesystem_tool import FilesystemTool


class TestFilesystemTool:
    """Testes para o FilesystemTool."""

    @pytest.fixture
    def tool(self):
        return FilesystemTool()

    @pytest.fixture
    def temp_dir(self):
        d = tempfile.mkdtemp()
        yield d
        shutil.rmtree(d, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_escrever_e_ler_arquivo(self, tool, temp_dir):
        path = os.path.join(temp_dir, "test.txt")

        result = await tool.execute({
            "action": "write",
            "path": path,
            "content": "Olá mundo",
        })
        assert result["success"] is True

        result = await tool.execute({
            "action": "read",
            "path": path,
        })
        assert result["success"] is True
        assert result["content"] == "Olá mundo"

    @pytest.mark.asyncio
    async def test_deletar_arquivo(self, tool, temp_dir):
        path = os.path.join(temp_dir, "test.txt")
        with open(path, "w") as f:
            f.write("conteúdo")

        result = await tool.execute({
            "action": "delete",
            "path": path,
        })
        assert result["success"] is True
        assert not os.path.exists(path)

    @pytest.mark.asyncio
    async def test_listar_diretorio(self, tool, temp_dir):
        os.makedirs(os.path.join(temp_dir, "subdir"))
        with open(os.path.join(temp_dir, "file.txt"), "w") as f:
            f.write("test")

        result = await tool.execute({
            "action": "list",
            "path": temp_dir,
        })
        assert result["success"] is True
        assert "file.txt" in result["entries"]
        assert "subdir" in result["entries"]

    @pytest.mark.asyncio
    async def test_arquivo_nao_encontrado(self, tool, temp_dir):
        result = await tool.execute({
            "action": "read",
            "path": os.path.join(temp_dir, "inexistente.txt"),
        })
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_rollback_escrita(self, tool, temp_dir):
        path = os.path.join(temp_dir, "test.txt")

        # Escrever conteúdo original
        with open(path, "w") as f:
            f.write("original")

        # Escrever novo conteúdo
        await tool.execute({
            "action": "write",
            "path": path,
            "content": "modificado",
        })

        # Verificar que foi modificado
        with open(path) as f:
            assert f.read() == "modificado"

        # Rollback
        await tool.rollback()

        # Verificar que voltou ao original
        with open(path) as f:
            assert f.read() == "original"

    @pytest.mark.asyncio
    async def test_rollback_delecao(self, tool, temp_dir):
        path = os.path.join(temp_dir, "test.txt")
        with open(path, "w") as f:
            f.write("conteúdo importante")

        # Deletar
        await tool.execute({
            "action": "delete",
            "path": path,
        })
        assert not os.path.exists(path)

        # Rollback
        await tool.rollback()

        # Verificar que o arquivo foi restaurado
        assert os.path.exists(path)

    @pytest.mark.asyncio
    async def test_validacao(self, tool):
        assert await tool.validate({"action": "read", "path": "/tmp/test"})
        assert await tool.validate({"action": "write", "path": "/tmp/test", "content": "x"})
        assert await tool.validate({"action": "delete", "path": "/tmp/test"})
        assert await tool.validate({"action": "list", "path": "/tmp"})
        assert not await tool.validate({"action": "invalid"})
        assert not await tool.validate({"action": "read"})
