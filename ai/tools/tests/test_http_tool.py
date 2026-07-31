"""Tests for the HTTPTool SSRF guard (CWE-918)."""

from __future__ import annotations

import pytest

from ai.tools.http_tool import HTTPTool


class TestHTTPTool:
    @pytest.mark.asyncio
    async def test_blocks_private_url(self) -> None:
        tool = HTTPTool()
        result = await tool.execute({"url": "http://169.254.169.254/latest/meta-data/"})
        assert result["success"] is False
        assert "internal" in result["error"]

    @pytest.mark.asyncio
    async def test_blocks_non_http_scheme(self) -> None:
        tool = HTTPTool()
        result = await tool.execute({"url": "file:///etc/passwd"})
        assert result["success"] is False
        assert "scheme" in result["error"]

    @pytest.mark.asyncio
    async def test_blocks_loopback(self) -> None:
        tool = HTTPTool()
        result = await tool.execute({"url": "http://127.0.0.1:8000/admin"})
        assert result["success"] is False
