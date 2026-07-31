"""Unit tests for auth.jwt module."""

from datetime import timedelta

import pytest

from backend.auth.jwt import JWTManager


@pytest.fixture
def jwt_manager():
    return JWTManager(secret_key="test-secret-key-for-unit-tests-2024")


class TestJWTManager:
    """Tests for JWT token creation and verification."""

    def test_initialization(self, jwt_manager):
        assert jwt_manager.ALGORITHM == "HS256"
        assert jwt_manager.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert jwt_manager.REFRESH_TOKEN_EXPIRE_MINUTES == 1440

    def test_reject_default_secret(self):
        with pytest.raises(ValueError, match="JWT_SECRET_KEY must be set"):
            JWTManager(secret_key="super-dev-secret-key-change-in-production")

    def test_reject_empty_secret(self):
        with pytest.raises(ValueError, match="JWT_SECRET_KEY must be set"):
            JWTManager(secret_key="")

    def test_create_access_token(self, jwt_manager):
        token = jwt_manager.create_access_token(subject="user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, jwt_manager):
        token = jwt_manager.create_refresh_token(subject="user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_access_token(self, jwt_manager):
        token = jwt_manager.create_access_token(subject="user-456")
        payload = jwt_manager.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-456"
        assert payload["type"] == "access"

    def test_decode_valid_refresh_token(self, jwt_manager):
        token = jwt_manager.create_refresh_token(subject="user-789")
        payload = jwt_manager.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-789"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self, jwt_manager):
        payload = jwt_manager.decode_token("invalid.token.here")
        assert payload is None

    def test_decode_tampered_token(self, jwt_manager):
        token = jwt_manager.create_access_token(subject="user-123")
        # Tamper with the token
        tampered = token[:-5] + "XXXXX"
        payload = jwt_manager.decode_token(tampered)
        assert payload is None

    def test_token_with_custom_expiry(self, jwt_manager):
        token = jwt_manager.create_access_token(
            subject="user-123",
            expires_delta=timedelta(minutes=5),
        )
        payload = jwt_manager.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_token_with_zero_expiry(self, jwt_manager):
        token = jwt_manager.create_access_token(
            subject="user-123",
            expires_delta=timedelta(seconds=0),
        )
        assert token == ""

    def test_different_tokens_different_subjects(self, jwt_manager):
        t1 = jwt_manager.create_access_token(subject="user-1")
        t2 = jwt_manager.create_access_token(subject="user-2")
        assert t1 != t2

        p1 = jwt_manager.decode_token(t1)
        p2 = jwt_manager.decode_token(t2)
        assert p1["sub"] == "user-1"
        assert p2["sub"] == "user-2"
