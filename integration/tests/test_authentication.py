"""Tests for the authentication subsystem (authentication/)."""

from __future__ import annotations

import pytest

from integration.authentication.api_key import APIKeyProvider
from integration.authentication.auth_engine import AuthEngine
from integration.authentication.certificate import CertificateManager
from integration.authentication.jwt import JWTProvider
from integration.authentication.oauth import OAuthProvider
from integration.authentication.secret_manager import SecretManager
from integration.authentication.token_manager import TokenManager


class TestJWTProvider:
    def test_encode_decode(self) -> None:
        jwt = JWTProvider(secret="test-secret")
        token = jwt.encode({"sub": "alice", "scopes": ["connections:connect"]})
        claims = jwt.decode(token)
        assert claims["sub"] == "alice"
        assert claims["scopes"] == ["connections:connect"]
        assert claims["exp"] > claims["iat"]

    def test_tamper_detection(self) -> None:
        jwt = JWTProvider(secret="test-secret")
        token = jwt.encode({"sub": "alice"})
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(ValueError):
            jwt.decode(tampered)

    def test_expiry(self) -> None:
        jwt = JWTProvider(secret="test-secret")
        token = jwt.encode({"sub": "alice"}, ttl=-10)  # already expired
        assert jwt.validate(token) is False
        with pytest.raises(ValueError):
            jwt.decode(token)

    def test_malformed(self) -> None:
        jwt = JWTProvider()
        assert jwt.validate("not-a-jwt") is False
        with pytest.raises(ValueError):
            jwt.decode("not-a-jwt")

    def test_different_secrets(self) -> None:
        a = JWTProvider(secret="secret-a")
        b = JWTProvider(secret="secret-b")
        token = a.encode({"sub": "x"})
        assert b.validate(token) is False


class TestOAuthProvider:
    def test_code_flow(self) -> None:
        oauth = OAuthProvider()
        oauth.register_client("client-1", "secret-1")
        code = oauth.authorize("client-1")
        token = oauth.exchange(code, "client-1", "secret-1")
        assert token.startswith("oauth-")
        assert oauth.validate(token) == "client-1"

    def test_unknown_client(self) -> None:
        oauth = OAuthProvider()
        with pytest.raises(KeyError):
            oauth.authorize("missing")

    def test_bad_credentials(self) -> None:
        oauth = OAuthProvider()
        oauth.register_client("c", "s")
        code = oauth.authorize("c")
        with pytest.raises(PermissionError):
            oauth.exchange(code, "c", "wrong")
        with pytest.raises(PermissionError):
            oauth.exchange("bad-code", "c", "s")

    def test_single_use_code(self) -> None:
        oauth = OAuthProvider()
        oauth.register_client("c", "s")
        code = oauth.authorize("c")
        oauth.exchange(code, "c", "s")
        with pytest.raises(PermissionError):
            oauth.exchange(code, "c", "s")

    def test_revoke(self) -> None:
        oauth = OAuthProvider()
        oauth.register_client("c", "s")
        token = oauth.exchange(oauth.authorize("c"), "c", "s")
        assert oauth.revoke(token) is True
        assert oauth.validate(token) is None


class TestAPIKeyProvider:
    def test_issue_validate(self) -> None:
        provider = APIKeyProvider()
        key = provider.issue("alice")
        assert key.startswith("sk-")
        assert provider.validate(key) == "alice"
        assert provider.validate("nope") is None

    def test_revoke(self) -> None:
        provider = APIKeyProvider()
        key = provider.issue("bob")
        assert provider.revoke(key) is True
        assert provider.validate(key) is None
        assert provider.revoke(key) is False

    def test_snapshot(self) -> None:
        provider = APIKeyProvider()
        provider.issue("alice")
        provider.issue("bob")
        assert provider.snapshot()["keys"] == 2


class TestTokenManager:
    def test_issue_validate(self) -> None:
        tokens = TokenManager(secret="s", ttl=3600)
        token = tokens.issue("alice", scopes=["read"])
        claims = tokens.validate(token)
        assert claims["sub"] == "alice"
        assert tokens.subject(token) == "alice"

    def test_revoke(self) -> None:
        tokens = TokenManager(secret="s")
        token = tokens.issue("alice")
        assert tokens.revoke(token) is True
        assert tokens.subject(token) is None
        with pytest.raises(ValueError):
            tokens.validate(token)
        assert tokens.revoke("bad-token") is False

    def test_refresh_flow(self) -> None:
        tokens = TokenManager(secret="s")
        refresh = tokens.create_refresh_token("alice")
        new_token = tokens.refresh(refresh)
        assert new_token is not None
        assert tokens.subject(new_token) == "alice"
        # refresh tokens are single-use
        assert tokens.refresh(refresh) is None


class TestCertificateManager:
    def test_register_get_remove(self) -> None:
        manager = CertificateManager()
        manager.register("prod", "-----BEGIN CERT-----", key="key", expires_at="2030-01-01")
        cert = manager.get("prod")
        assert cert is not None
        assert cert["certificate"].startswith("-----BEGIN CERT")
        assert cert["expires_at"] == "2030-01-01"
        assert manager.has("prod") is True
        assert manager.remove("prod") is True
        assert manager.remove("prod") is False

    def test_rotate(self) -> None:
        manager = CertificateManager()
        assert manager.rotate("missing", "x") is False
        manager.register("a", "cert-1")
        assert manager.rotate("a", "cert-2") is True
        cert = manager.get("a")
        assert cert is not None
        assert cert["certificate"] == "cert-2"


class TestSecretManager:
    def test_store_get_delete(self) -> None:
        manager = SecretManager()
        manager.store("db_password", "s3cret")
        assert manager.get("db_password") == "s3cret"
        assert manager.exists("db_password") is True
        assert manager.delete("db_password") is True
        assert manager.delete("db_password") is False

    def test_generate_and_rotate(self) -> None:
        manager = SecretManager()
        value = manager.generate("api_secret", length=24)
        assert len(value) == 24
        assert manager.get("api_secret") == value
        rotated = manager.rotate("api_secret")
        assert rotated != value
        assert manager.rotate("missing") is None

    def test_snapshot(self) -> None:
        manager = SecretManager()
        manager.store("a", "1")
        manager.store("b", "2")
        assert manager.snapshot()["secrets"] == 2
        assert manager.list_names() == ["a", "b"]


class TestAuthEngine:
    def test_authenticate_api_key(self) -> None:
        engine = AuthEngine()
        key = engine.api_keys.issue("alice")
        result = engine.authenticate("api_key", {"api_key": key})
        assert result == key
        assert engine.validate("api_key", key) is True

    def test_authenticate_jwt_and_token(self) -> None:
        engine = AuthEngine()
        token = engine.authenticate("token", {"subject": "alice", "scopes": ["read"]})
        assert engine.validate("token", token) is True
        jwt_token = engine.authenticate("jwt", {"token": token})
        assert engine.validate("jwt", jwt_token) is True

    def test_authenticate_oauth(self) -> None:
        engine = AuthEngine()
        engine.oauth.register_client("c", "s")
        code = engine.oauth.authorize("c")
        token = engine.authenticate("oauth", {"code": code, "client_id": "c", "client_secret": "s"})
        assert engine.validate("oauth", token) is True

    def test_unknown_method(self) -> None:
        engine = AuthEngine()
        with pytest.raises(ValueError):
            engine.authenticate("weird", {})
        with pytest.raises(ValueError):
            engine.validate("weird", "x")

    def test_stats(self) -> None:
        engine = AuthEngine()
        engine.api_keys.issue("alice")
        engine.secrets.store("k", "v")
        engine.certificates.register("c", "cert")
        stats = engine.stats()
        assert stats["api_keys"] == 1
        assert stats["secrets"] == 1
        assert stats["certificates"] == 1
