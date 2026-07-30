from __future__ import annotations

import json
import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.rest import RESTfulServer, RESTRouter, RequestParser, ResponseBuilder  # noqa: E402
from api.rest.pagination import Pagination  # noqa: E402
from api.rest.streaming import StreamingResponse  # noqa: E402


class TestRESTfulServer:
    def test_server_initialization(self) -> None:
        server = RESTfulServer("0.0.0.0", 8080)
        assert server.host == "0.0.0.0"
        assert server.port == 8080

    def test_server_routes(self) -> None:
        server = RESTfulServer("0.0.0.0", 8080)
        router = server.router
        assert isinstance(router, RESTRouter)


class TestRESTRouter:
    def test_route_registration(self) -> None:
        router = RESTRouter(None)
        router.register("GET", "/test", None)
        assert len(router.routes) == 1

    def test_route_params(self) -> None:
        router = RESTRouter(None)
        params = router.extract_params("/users/{id}", "/users/42")
        assert params == {"id": "42"}

    def test_route_params_no_match(self) -> None:
        router = RESTRouter(None)
        params = router.extract_params("/users/{id}", "/posts/42")
        assert params is None


class TestRequestParser:
    def test_parse_json_body(self) -> None:
        parser = RequestParser()
        body = json.dumps({"key": "value"}).encode()
        data = parser.parse_json(body)
        assert data == {"key": "value"}

    def test_parse_query_string(self) -> None:
        parser = RequestParser()
        params = parser.parse_query("foo=1&bar=hello")
        assert params == {"foo": "1", "bar": "hello"}

    def test_parse_empty_query(self) -> None:
        parser = RequestParser()
        params = parser.parse_query("")
        assert params == {}


class TestResponseBuilder:
    def test_build_json_response(self) -> None:
        builder = ResponseBuilder()
        data = {"message": "ok"}
        response = builder.json(data, status=200)
        assert response["status"] == 200
        assert json.loads(response["body"]) == data

    def test_build_error_response(self) -> None:
        builder = ResponseBuilder()
        response = builder.error(404, "Not Found")
        assert response["status"] == 404

    def test_build_empty_response(self) -> None:
        builder = ResponseBuilder()
        response = builder.empty(204)
        assert response["status"] == 204


class TestPagination:
    def test_paginate(self) -> None:
        items = [1, 2, 3, 4, 5]
        pagination = Pagination()
        result = pagination.paginate(items, page=1, per_page=2)
        assert result.items == [1, 2]
        assert result.page == 1
        assert result.per_page == 2
        assert result.total == 5

    def test_paginate_page_2(self) -> None:
        items = [1, 2, 3, 4, 5]
        pagination = Pagination()
        result = pagination.paginate(items, page=2, per_page=2)
        assert result.items == [3, 4]

    def test_paginate_last_page(self) -> None:
        items = [1, 2, 3, 4, 5]
        pagination = Pagination()
        result = pagination.paginate(items, page=3, per_page=2)
        assert result.items == [5]

    def test_paginate_empty(self) -> None:
        pagination = Pagination()
        result = pagination.paginate([], page=1, per_page=10)
        assert result.items == []
        assert result.total == 0


class TestStreamingResponse:
    def test_streaming_init(self) -> None:
        stream = StreamingResponse()
        assert stream is not None

    def test_streaming_chunks(self) -> None:
        stream = StreamingResponse()
        chunks = list(stream.iterate([{"id": 1}, {"id": 2}]))
        assert len(chunks) == 2
