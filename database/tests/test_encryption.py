from __future__ import annotations

import pytest  # type: ignore[import-untyped]

from SuperDev.database.encryption import DatabaseEncryption, DecryptionError, EncryptionField


class TestDatabaseEncryption:
    @pytest.fixture()
    def enc(self) -> DatabaseEncryption:
        return DatabaseEncryption(master_key="test-key-001")

    def test_roundtrip(self, enc: DatabaseEncryption) -> None:
        ct = enc.encrypt("hello world")
        pt = enc.decrypt(ct)
        assert pt == "hello world"

    def test_empty_string(self, enc: DatabaseEncryption) -> None:
        assert enc.encrypt("") == ""
        assert enc.decrypt("") == ""

    def test_different_keys(self) -> None:
        e1 = DatabaseEncryption(master_key="key-a")
        e2 = DatabaseEncryption(master_key="key-b")
        ct = e1.encrypt("secret")
        with pytest.raises(DecryptionError):
            e2.decrypt(ct)

    def test_key_fingerprint(self, enc: DatabaseEncryption) -> None:
        fp = enc.key_fingerprint
        assert len(fp) == 16
        assert isinstance(fp, str)

    def test_unicode(self, enc: DatabaseEncryption) -> None:
        original = "café 🎉"
        ct = enc.encrypt(original)
        pt = enc.decrypt(ct)
        assert pt == original


class TestEncryptionField:
    def test_field_encrypts_on_set(self) -> None:
        enc = DatabaseEncryption(master_key="field-test")
        field = EncryptionField(encryption=enc)
        field.name = "ssn"

        class FakeModel:
            _values: dict = {}

        obj = FakeModel()
        field.__set__(obj, "123-45-6789")
        raw = obj._values["ssn"]
        # raw should be base64 ciphertext, not plaintext
        assert raw != "123-45-6789"
        assert isinstance(raw, str)

        # reading back should decrypt
        decrypted = field.__get__(obj)
        assert decrypted == "123-45-6789"

    def test_field_none(self) -> None:
        field = EncryptionField()
        field.name = "secret"

        class FakeModel:
            _values: dict = {}

        obj = FakeModel()
        field.__set__(obj, None)
        assert field.__get__(obj) is None
