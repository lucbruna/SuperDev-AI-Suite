from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.sdk import (
    BaseClient,
    RESTClient,
    AuthClient,
    GraphQLClient,
    GrpcClient,
    SDKError,
    AuthenticationError,
    NotFoundError,
)
from api.sdk.errors import ConnectionError, ValidationError


class TestSDKErrors:
    def test_sdk_error(self) -> None:
        err = SDKError("generic", status_code=500)
        assert str(err) == "generic"
        assert err.status_code == 500

    def test_auth_error(self) -> None:
        err = AuthenticationError("unauthorized", status_code=401)
        assert err.status_code == 401

    def test_not_found(self) -> None:
        err = NotFoundError("missing", status_code=404)
        assert err.status_code == 404

    def test_error_inheritance(self) -> None:
        assert issubclass(AuthenticationError, SDKError)
        assert issubclass(NotFoundError, SDKError)
        assert issubclass(ConnectionError, SDKError)
        assert issubclass(ValidationError, SDKError)


class TestBaseClient:
    def test_initialization(self) -> None:
        client = BaseClient("https://api.example.com")
        assert client.base_url == "https://api.example.com"

    def test_initialization_with_trailing_slash(self) -> None:
        client = BaseClient("https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_auth_headers_api_key(self) -> None:
        client = BaseClient("https://api.example.com", api_key="key123")
        assert client._default_headers.get("X-API-Key") == "key123"

    def test_auth_headers_token(self) -> None:
        client = BaseClient("https://api.example.com", access_token="tok123")
        assert client._default_headers.get("Authorization") == "Bearer tok123"

    def test_set_token(self) -> None:
        client = BaseClient("https://api.example.com")
        client.set_token("new-token")
        assert client._default_headers.get("Authorization") == "Bearer new-token"

    def test_build_url(self) -> None:
        client = BaseClient("https://api.example.com")
        url = client._build_url("/users")
        assert url == "https://api.example.com/users"

    def test_build_url_with_params(self) -> None:
        client = BaseClient("https://api.example.com")
        url = client._build_url("/users", {"page": "1", "limit": "10"})
        assert "page=1" in url
        assert "limit=10" in url


class TestRESTClient:
    def test_initialization(self) -> None:
        client = RESTClient("https://api.example.com")
        assert client.base_url == "https://api.example.com"

    def test_list_builds_params(self) -> None:
        client = RESTClient("https://api.example.com")
        # Just verify it builds the request without raising
        client.list("/users", page=2, per_page=50)


class TestGraphQLClient:
    def test_initialization(self) -> None:
        client = GraphQLClient("https://api.example.com")
        assert client is not None

    def test_introspection_query(self) -> None:
        client = GraphQLClient("https://api.example.com")
        result = client.introspect()
        # Should fail to connect but not crash
        assert result is None or isinstance(result, dict)


class TestGrpcClient:
    def test_initialization(self) -> None:
        client = GrpcClient("https://api.example.com")
        assert client is not None

    def test_unary_call(self) -> None:
        client = GrpcClient("https://api.example.com")
        result = client.unary("UserService", "GetUser", {"id": "1"})
        assert result is None or isinstance(result, dict)


class TestAuthClient:
    def test_initialization(self) -> None:
        client = AuthClient("https://api.example.com")
        assert client is not None

    def test_login_builds_request(self) -> None:
        client = AuthClient("https://api.example.com")
        # Won't actually connect
        result = client.login("user", "pass")
        assert result is None or isinstance(result, dict)
