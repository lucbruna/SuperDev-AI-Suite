"""Tests for the encryption, hashing and signatures subsystems."""

from __future__ import annotations

from SuperDev.security.security_engine import SecurityEngine


class TestEncryption:
    def test_roundtrip(self, engine: SecurityEngine) -> None:
        key = engine.encryption.generate_key()
        payload = engine.encryption.encrypt("mensagem secreta", key)
        assert engine.encryption.decrypt(payload, key) == "mensagem secreta"
        assert engine.metrics.get_counter("security.encryptions") >= 1

    def test_different_keys_fail(self, engine: SecurityEngine) -> None:
        key_a = engine.encryption.generate_key()
        key_b = engine.encryption.generate_key()
        payload = engine.encryption.encrypt("x", key_a)
        # Decrypting with the wrong key yields garbled text (not the original).
        assert engine.encryption.decrypt(payload, key_b) != "x"

    def test_encrypt_uses_generated_key(self, engine: SecurityEngine) -> None:
        engine.encryption.generate_key()
        payload = engine.encryption.encrypt("auto")
        assert payload.ciphertext


class TestHashing:
    def test_digest_consistency(self, engine: SecurityEngine) -> None:
        first = engine.hashing.digest("dado")
        second = engine.hashing.digest("dado")
        assert first.digest == second.digest
        assert len(first.digest) == 64  # sha256

    def test_verify_digest(self, engine: SecurityEngine) -> None:
        digest = engine.hashing.digest("dado")
        assert engine.hashing.verify_digest("dado", digest.digest)
        assert not engine.hashing.verify_digest("outro", digest.digest)

    def test_password_hash_and_verify(self, engine: SecurityEngine) -> None:
        result = engine.hashing.hash_password("SenhaForte!1", iterations=1000)
        assert result.salt
        assert engine.hashing.verify_password("SenhaForte!1", result)
        assert not engine.hashing.verify_password("senha-errada", result)

    def test_hmac(self, engine: SecurityEngine) -> None:
        key = b"chave"
        mac = engine.hashing.hmac_digest(key, "mensagem")
        assert mac == engine.hashing.hmac_digest(key, "mensagem")
        assert mac != engine.hashing.hmac_digest(key, "outra")


class TestSignatures:
    def test_sign_and_verify(self, engine: SecurityEngine) -> None:
        key = engine.signatures.generate_key()
        signed = engine.signatures.sign("payload", key)
        result = engine.signatures.verify("payload", signed.signature, key)
        assert result.valid is True

    def test_tampered_fails(self, engine: SecurityEngine) -> None:
        key = engine.signatures.generate_key()
        signed = engine.signatures.sign("payload", key)
        result = engine.signatures.verify("outro-payload", signed.signature, key)
        assert result.valid is False
