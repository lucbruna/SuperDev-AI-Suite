"""Unit tests for the API key auth fix (finding 2f29e692, HIGH).

Validates that ``_generate_api_key`` / ``_verify_api_key`` now:
* store a 24-char prefix that matches the ``APIKeyAuth`` lookup slice
  (``token[:24]`` in backend/auth/manager.py), so keys can actually be found;
* hash with bcrypt (the same scheme ``APIKeyAuth`` verifies with via
  ``verify_password``), so a found key can actually authenticate;
* fit the widened ``api_keys.key_prefix`` column (String(32)).
"""

from __future__ import annotations

import hashlib
import secrets

from backend.api.v1 import api_keys as api_keys_module
from backend.api.v1.api_keys import _generate_api_key, _verify_api_key
from backend.auth.passwords import verify_password
from backend.database.models.api_key import API_KEY_PREFIX_LENGTH

# The exact lookup slice used by APIKeyAuth.__call__ (backend/auth/manager.py) —
# sourced from the shared constant so the test cannot drift from the code.
MANAGER_LOOKUP_LENGTH = API_KEY_PREFIX_LENGTH


class TestGenerateApiKey:
    def test_returns_three_parts(self):
        raw, key_hash, prefix = _generate_api_key()
        assert isinstance(raw, str)
        assert isinstance(key_hash, str)
        assert isinstance(prefix, str)

    def test_raw_key_format(self):
        raw, _, _ = _generate_api_key()
        assert raw.startswith("sk_")
        assert len(raw) > 24

    def test_prefix_matches_manager_lookup_slice(self):
        """The stored prefix must equal raw[:24] — APIKeyAuth's token[:24] lookup."""
        raw, _, prefix = _generate_api_key()
        assert prefix == raw[:MANAGER_LOOKUP_LENGTH]

    def test_prefix_length_matches_manager(self):
        _, _, prefix = _generate_api_key()
        assert len(prefix) == MANAGER_LOOKUP_LENGTH

    def test_prefix_fits_widened_column(self):
        """String(32) must be able to hold the 24-char prefix (regression guard)."""
        from backend.database.models.api_key import APIKey

        column = APIKey.__table__.c.key_prefix
        assert column.type.length >= MANAGER_LOOKUP_LENGTH

    def test_hash_is_bcrypt(self):
        """Storage hash must be bcrypt (what the auth manager verifies with)."""
        _, key_hash, _ = _generate_api_key()
        assert key_hash.startswith("$2")

    def test_hash_verifies_with_manager_scheme(self):
        """verify_password (the manager's check) must accept our generated hash."""
        raw, key_hash, _ = _generate_api_key()
        assert verify_password(raw, key_hash) is True


class TestVerifyApiKey:
    def test_verify_correct_key(self):
        raw, key_hash, _ = _generate_api_key()
        assert _verify_api_key(raw, key_hash) is True

    def test_verify_wrong_key(self):
        _, key_hash, _ = _generate_api_key()
        wrong = "sk_" + secrets.token_hex(32)
        assert _verify_api_key(wrong, key_hash) is False

    def test_verify_wrong_hash(self):
        raw, _, _ = _generate_api_key()
        other_hash = api_keys_module._generate_api_key()[1]
        assert _verify_api_key(raw, other_hash) is False

    def test_verify_rejects_sha256_hex(self):
        """A legacy SHA-256 hex digest must NOT verify as bcrypt."""
        raw, _, _ = _generate_api_key()
        legacy_sha256 = hashlib.sha256(raw.encode()).hexdigest()
        assert _verify_api_key(raw, legacy_sha256) is False


class TestRoundTrip:
    def test_generate_then_verify_roundtrip(self):
        for _ in range(5):
            raw, key_hash, prefix = _generate_api_key()
            assert prefix == raw[:MANAGER_LOOKUP_LENGTH]
            assert _verify_api_key(raw, key_hash) is True
