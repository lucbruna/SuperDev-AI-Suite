from __future__ import annotations

from datetime import timedelta

from backend.auth.jwt import JWTManager
from backend.auth.passwords import hash_password, verify_password


class TestPasswordHashing:
    def test_hash_password_returns_string(self) -> None:
        hashed = hash_password("securePassword123")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_differs_from_original(self) -> None:
        password = "securePassword123"
        hashed = hash_password(password)
        assert hashed != password

    def test_verify_password_correct(self) -> None:
        password = "securePassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self) -> None:
        hashed = hash_password("securePassword123")
        assert verify_password("wrongPassword", hashed) is False

    def test_hash_generates_unique_salts(self) -> None:
        password = "securePassword123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)
        assert hashed1 != hashed2

    def test_verify_password_with_empty_string(self) -> None:
        hashed = hash_password("nonempty")
        assert verify_password("", hashed) is False

    def test_verify_password_with_unicode(self) -> None:
        password = "pässwörd🔐"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWTToken:
    def setup_method(self) -> None:
        self.manager = JWTManager(secret_key="test-secret-key-for-testing")

    def test_create_access_token_returns_string(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_parts(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        parts = token.split(".")
        assert len(parts) == 3

    def test_decode_valid_token(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        payload = self.manager.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_decode_token_with_custom_subject(self) -> None:
        token = self.manager.create_access_token(subject="custom-subject-456")
        payload = self.manager.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "custom-subject-456"

    def test_create_refresh_token(self) -> None:
        token = self.manager.create_refresh_token(subject="user-123")
        payload = self.manager.decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user-123"

    def test_decode_invalid_token(self) -> None:
        result = self.manager.decode_token("invalid.token.here")
        assert result is None

    def test_decode_token_with_wrong_secret(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        wrong_manager = JWTManager(secret_key="different-secret-key")
        result = wrong_manager.decode_token(token)
        assert result is None

    def test_decode_tampered_token(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        parts = token.split(".")
        parts[1] = "eyJzdWIiOiJoYWNrZWQifQ"
        tampered = ".".join(parts)
        result = self.manager.decode_token(tampered)
        assert result is None

    def test_token_expiration(self) -> None:
        token = self.manager.create_access_token(
            subject="user-123",
            expires_delta=timedelta(seconds=-1),
        )
        payload = self.manager.decode_token(token)
        assert payload is None

    def test_token_with_zero_expiration(self) -> None:
        token = self.manager.create_access_token(
            subject="user-123",
            expires_delta=timedelta(seconds=0),
        )
        payload = self.manager.decode_token(token)
        assert payload is None

    def test_token_contains_iat_claim(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        payload = self.manager.decode_token(token)
        assert payload is not None
        assert "iat" in payload

    def test_token_contains_exp_claim(self) -> None:
        token = self.manager.create_access_token(subject="user-123")
        payload = self.manager.decode_token(token)
        assert payload is not None
        assert "exp" in payload
