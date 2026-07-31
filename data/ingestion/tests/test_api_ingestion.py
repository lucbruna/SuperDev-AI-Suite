from __future__ import annotations

import pytest

from SuperDev.data.ingestion.api_ingestion import APICollector, APIConnector


class TestAPIConnector:
    @pytest.mark.asyncio
    async def test_read_list_payload(self, monkeypatch) -> None:
        connector = APIConnector("api", {"url": "https://example.com/data"})

        def fake_request(url, _method, _headers, _timeout, _body):
            assert "example.com/data" in url
            return [{"id": 1}, {"id": 2}]  # parsed JSON, as real _request returns

        monkeypatch.setattr(connector, "_request", fake_request)
        assert await connector.connect()
        rows = await connector.read()
        assert len(rows) == 2
        assert rows[0]["id"] == 1
        await connector.disconnect()

    @pytest.mark.asyncio
    async def test_read_wrapped_payload(self, monkeypatch) -> None:
        connector = APIConnector("api", {"url": "https://example.com/data"})
        monkeypatch.setattr(connector, "_request", lambda *_a, **_k: {"results": [{"x": 10}]})
        await connector.connect()
        rows = await connector.read()
        assert rows == [{"x": 10}]

    @pytest.mark.asyncio
    async def test_read_with_pagination(self, monkeypatch) -> None:
        connector = APIConnector(
            "api",
            {"url": "https://example.com/data", "pagination": {"param": "page", "per_page": 2}},
        )
        pages = [
            [{"id": 1}, {"id": 2}],
            [{"id": 3}],
        ]

        def fake_request(url, _method, _headers, _timeout, _body):
            page = int(url.split("page=")[1])
            return pages[page - 1]

        monkeypatch.setattr(connector, "_request", fake_request)
        await connector.connect()
        rows = await connector.read()
        assert len(rows) == 3
        assert rows[-1]["id"] == 3

    @pytest.mark.asyncio
    async def test_pagination_respects_max_pages(self, monkeypatch) -> None:
        connector = APIConnector(
            "api",
            {"url": "https://example.com/data", "pagination": {"param": "page", "per_page": 2}},
        )

        def fake_request(*_args, **_kwargs):
            # Server ignores the page param and always returns a full page
            return [{"id": 1}, {"id": 2}]

        monkeypatch.setattr(connector, "_request", fake_request)
        await connector.connect()
        with pytest.raises(ValueError, match="max_pages"):
            await connector.read({"max_pages": 3})

    @pytest.mark.asyncio
    async def test_connect_requires_url(self) -> None:
        connector = APIConnector("api", {})
        assert await connector.connect() is False

    @pytest.mark.asyncio
    async def test_read_without_url_raises(self) -> None:
        connector = APIConnector("api", {})
        await connector.connect()
        with pytest.raises(ValueError):
            await connector.read()

    @pytest.mark.asyncio
    async def test_blocks_ssrf_private_url(self) -> None:
        # CWE-918 regression: cloud metadata / private targets must be refused
        # before any network call happens.
        connector = APIConnector(
            "api", {"url": "http://169.254.169.254/latest/meta-data/"})
        await connector.connect()
        with pytest.raises(ValueError, match="internal"):
            await connector.read()

    @pytest.mark.asyncio
    async def test_blocks_ssrf_loopback(self) -> None:
        connector = APIConnector("api", {"url": "http://127.0.0.1:8000/admin"})
        await connector.connect()
        with pytest.raises(ValueError, match="internal"):
            await connector.read()

    @pytest.mark.asyncio
    async def test_allow_private_urls_opt_in(self, monkeypatch) -> None:
        # With the opt-in flag the guard passes and the fetch proceeds.
        # _request is monkeypatched so no real socket is ever touched.
        connector = APIConnector(
            "api",
            {"url": "http://127.0.0.1:8000/data", "allow_private_urls": True},
        )
        monkeypatch.setattr(connector, "_request", lambda *_a, **_k: [{"id": 1}])
        await connector.connect()
        rows = await connector.read()
        assert rows == [{"id": 1}]


class TestAPICollector:
    @pytest.mark.asyncio
    async def test_collect_builds_batch(self, monkeypatch) -> None:
        connector = APIConnector("api", {"url": "https://example.com/data"})
        monkeypatch.setattr(connector, "_request", lambda *_a, **_k: [{"id": 1}, {"id": 2}])
        collector = APICollector("api-source", connector=connector)
        batch = await collector.collect()
        assert batch.source == "api-source"
        assert len(batch.records) == 2
        assert batch.records[0].data["id"] == 1
        assert connector.connected is False  # disconnected after collect
