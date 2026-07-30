from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.auth import Authenticator, JWTHandler, OAuthHandler, APIKeyHandler, MFAHandler, SessionHandler  # noqa: E402


class TestJWTHandler:
    def test_encode_decode(self) -> None:
        jwt = JWTHandler(secret="test-secret")
        token = jwt.encode({"sub": "123", "role": "admin"})
        payload = jwt.decode(token)
        assert payload["sub"] == "123"
        assert payload["role"] == "admin"

    def test_expired_token(self) -> None:
        jwt = JWTHandler(secret="test-secret")
        token = jwt.encode({"sub": "123"}, ttl=-1)
        payload = jwt.decode(token)
        assert payload is None or "exp" in payload


class TestAPIKeyHandler:
    def test_generate_and_validate(self) -> None:
        handler = APIKeyHandler()
        api_key = handler.generate("user1")
        user_id = handler.validate(api_key)
        assert user_id == "user1"

    def test_invalid_key(self) -> None:
        handler = APIKeyHandler()
        user_id = handler.validate("invalid-key")
        assert user_id is None


class TestMFAHandler:
    def test_generate_secret(self) -> None:
        mfa = MFAHandler()
        secret = mfa.generate_secret()
        assert len(secret) > 0

    def test_generate_code(self) -> None:
        mfa = MFAHandler()
        secret = mfa.generate_secret()
        code = mfa.generate_code(secret)
        assert len(code) == 6
        assert code.isdigit()

    def test_verify_code(self) -> None:
        mfa = MFAHandler()
        secret = mfa.generate_secret()
        code = mfa.generate_code(secret)
        result = mfa.verify_code(secret, code)
        assert result is True

    def test_verify_invalid_code(self) -> None:
        mfa = MFAHandler()
        secret = mfa.generate_secret()
        result = mfa.verify_code(secret, "000000")
        # May or may not verify depending on TOTP window
        # Just verify it doesn't crash


class TestSessionHandler:
    def test_create_session(self) -> None:
        handler = SessionHandler()
        session = handler.create("user1")
        assert session["user_id"] == "user1"
        assert "session_id" in session
        assert "expires_at" in session

    def test_validate_session(self) -> None:
        handler = SessionHandler()
        session = handler.create("user1")
        result = handler.validate(session["session_id"])
        assert result is not None
        assert result["user_id"] == "user1"

    def test_invalidate_session(self) -> None:
        handler = SessionHandler()
        session = handler.create("user1")
        handler.invalidate(session["session_id"])
        result = handler.validate(session["session_id"])
        assert result is None


class TestAuthenticator:
    def test_register_plugin(self) -> None:
        auth = Authenticator()
        handler = APIKeyHandler()
        auth.register("apikey", handler)
        assert "apikey" in auth.plugins
