"""Tests for the SSRF guard helpers (CWE-918)."""

from __future__ import annotations

import pytest

from security.ssrf import is_internal_host, validate_public_url


class TestValidatePublicUrl:
    def test_allows_public_https(self) -> None:
        assert validate_public_url("https://example.com/api") == \
            "https://example.com/api"

    def test_allows_public_http(self) -> None:
        assert validate_public_url("http://example.com/api") == \
            "http://example.com/api"

    def test_allows_public_ipv4(self) -> None:
        assert validate_public_url("http://8.8.8.8/path") == \
            "http://8.8.8.8/path"

    @pytest.mark.parametrize("url", [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://127.0.0.1:8080/admin",
        "http://10.0.0.5/data",
        "http://172.16.0.1/",
        "http://192.168.1.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://0.0.0.0/",
        "http://[::1]/",
    ])
    def test_blocks_internal(self, url: str) -> None:
        with pytest.raises(ValueError, match="internal"):
            validate_public_url(url)

    def test_blocks_non_http_scheme(self) -> None:
        with pytest.raises(ValueError, match="scheme"):
            validate_public_url("ftp://example.com/file")

    def test_blocks_missing_host(self) -> None:
        with pytest.raises(ValueError, match="no host"):
            validate_public_url("http:///path")

    def test_allow_private_opt_in(self) -> None:
        assert validate_public_url("http://127.0.0.1/", allow_private=True) == \
            "http://127.0.0.1/"


class TestIsInternalHost:
    def test_literal_loopback(self) -> None:
        assert is_internal_host("127.0.0.1") is True

    def test_literal_public(self) -> None:
        assert is_internal_host("8.8.8.8") is False

    def test_localhost_hostname(self) -> None:
        assert is_internal_host("localhost") is True

    def test_private_ranges(self) -> None:
        assert is_internal_host("192.168.1.1") is True
        assert is_internal_host("169.254.169.254") is True
        assert is_internal_host("10.0.0.5") is True
