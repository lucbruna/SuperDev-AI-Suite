"""Tests for the RuntimeFilesystem sandbox (path-traversal guard, CWE-22)."""

from __future__ import annotations

import pytest

from core.runtime.filesystem.filesystem import RuntimeFilesystem


class TestRuntimeFilesystem:
    @pytest.mark.asyncio
    async def test_write_and_read(self, tmp_path) -> None:
        fs = RuntimeFilesystem(tmp_path)
        await fs.write_file("run1", "src/a.py", "x = 1")
        assert await fs.read_file("run1", "src/a.py") == "x = 1"

    @pytest.mark.asyncio
    async def test_path_traversal_read_blocked(self, tmp_path) -> None:
        fs = RuntimeFilesystem(tmp_path)
        await fs.write_file("run1", "ok.txt", "fine")
        with pytest.raises(ValueError, match="escapes"):
            await fs.read_file("run1", "../secret.txt")

    @pytest.mark.asyncio
    async def test_path_traversal_write_blocked(self, tmp_path) -> None:
        fs = RuntimeFilesystem(tmp_path)
        with pytest.raises(ValueError, match="escapes"):
            await fs.write_file("run1", "../../evil.txt", "x")

    @pytest.mark.asyncio
    async def test_path_traversal_list_blocked(self, tmp_path) -> None:
        fs = RuntimeFilesystem(tmp_path)
        await fs.write_file("run1", "ok.txt", "fine")
        with pytest.raises(ValueError, match="escapes"):
            await fs.list_files("run1", "..")

    @pytest.mark.asyncio
    async def test_session_isolation(self, tmp_path) -> None:
        fs = RuntimeFilesystem(tmp_path)
        await fs.write_file("run1", "a.txt", "sessao 1")
        # Another session cannot reach run1's files via traversal.
        with pytest.raises(ValueError, match="escapes"):
            await fs.read_file("run2", "../run1/a.txt")
