"""Unit tests for auth.passwords module."""

import pytest

from backend.auth.passwords import hash_password, verify_password


class TestHashPassword:
    """Tests for password hashing."""

    def test_hash_password_returns_string(self):
        result = hash_password("testpassword123")
        assert isinstance(result, str)

    def test_hash_password_is_bcrypt_format(self):
        result = hash_password("testpassword123")
        assert result.startswith("$2")

    def test_hash_password_different_each_time(self):
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2

    def test_hash_password_with_unicode(self):
        result = hash_password("pässwörd123")
        assert isinstance(result, str)
        assert len(result) > 0


class TestVerifyPassword:
    """Tests for password verification."""

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_verify_unicode_password(self):
        hashed = hash_password("pässwörd")
        assert verify_password("pässwörd", hashed) is True
        assert verify_password("password", hashed) is False

    def test_hash_then_verify_roundtrip(self):
        passwords = [
            "simple",
            "complex!@#$%^&*()",
            "a" * 72,  # bcrypt max is 72 bytes
            "unicode_test",
        ]
        for pwd in passwords:
            hashed = hash_password(pwd)
            assert verify_password(pwd, hashed), f"Roundtrip failed for: {pwd!r}"

    def test_long_password_is_truncated_to_72_bytes(self):
        """bcrypt 4.3.0 silently truncates passwords > 72 bytes (no error)."""
        long_pwd = "x" * 200
        hashed = hash_password(long_pwd)
        assert isinstance(hashed, str)
        assert hashed.startswith("$2")
        # checkpw truncates the same way, so a >72-byte input still verifies
        # against a hash produced from the same input.
        assert verify_password(long_pwd, hashed) is True

    def test_password_at_bcrypt_limit(self):
        """Exactly 72 bytes should work fine."""
        pwd_72 = "a" * 72
        hashed = hash_password(pwd_72)
        assert verify_password(pwd_72, hashed) is True
