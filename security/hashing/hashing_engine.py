"""Hashing subsystem (Volume 16) — digests, salted password hashing, HMAC."""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any

from ..security_models import HashAlgorithm, HashResult


class HashingEngine:
    """Digest + salted password hashing with constant-time verification."""

    name = "hashing"
    description = "Digests, salted password hashing, HMAC"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine

    def digest(self, data: str | bytes, algorithm: HashAlgorithm | str = HashAlgorithm.SHA256) -> HashResult:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        algo = HashAlgorithm(algorithm) if isinstance(algorithm, str) else algorithm
        if algo == HashAlgorithm.SHA512:
            digest = hashlib.sha512(raw).hexdigest()
        elif algo == HashAlgorithm.BLAKE2B:
            digest = hashlib.blake2b(raw).hexdigest()
        else:
            digest = hashlib.sha256(raw).hexdigest()
        if self.engine is not None:
            self.engine.metrics.increment("security.hashes")
        return HashResult(digest=digest, algorithm=algo.value)

    def verify_digest(
        self,
        data: str | bytes,
        digest: str,
        algorithm: HashAlgorithm | str = HashAlgorithm.SHA256,
    ) -> bool:
        return hmac.compare_digest(self.digest(data, algorithm).digest, digest)

    def hash_password(self, password: str, iterations: int = 100_000, salt: bytes | None = None) -> HashResult:
        """Iteratively hash a password with a random salt (PBKDF2-style)."""
        salt = salt or os.urandom(16)
        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, max(1, iterations)
        ).hex()
        if self.engine is not None:
            self.engine.metrics.increment("security.password_hashes")
        return HashResult(
            digest=derived,
            algorithm="pbkdf2-sha256",
            salt=salt.hex(),
            iterations=max(1, iterations),
        )

    def verify_password(self, password: str, result: HashResult | dict[str, Any]) -> bool:
        if isinstance(result, dict):
            result = HashResult(
                digest=result["digest"],
                algorithm=result.get("algorithm", "pbkdf2-sha256"),
                salt=result.get("salt", ""),
                iterations=int(result.get("iterations", 1)),
            )
        expected = self.hash_password(
            password, iterations=result.iterations, salt=bytes.fromhex(result.salt)
        )
        return hmac.compare_digest(expected.digest, result.digest)

    def hmac_digest(self, key: bytes, data: str | bytes) -> str:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        if self.engine is not None:
            self.engine.metrics.increment("security.hmacs")
        return hmac.new(key, raw, hashlib.sha256).hexdigest()

    def status(self) -> dict[str, Any]:
        return {"algorithm": "sha256/pbkdf2-sha256", "supported": [a.value for a in HashAlgorithm]}
