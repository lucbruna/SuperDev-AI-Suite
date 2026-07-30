from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import struct
import time
from typing import Any

from ..api_interfaces import IAPIAuthenticator


class MFAHandler(IAPIAuthenticator):
    """Multi-factor authentication (TOTP) handler."""

    def __init__(self, drift_steps: int = 1, step_seconds: int = 30) -> None:
        self._drift_steps = drift_steps
        self._step_seconds = step_seconds
        self._used_codes: set[str] = set()
        self._recovery_codes: dict[str, bool] = {}

    def generate_totp_secret(self) -> str:
        return base64.b32encode(os.urandom(20)).decode("utf-8")

    def generate_totp_code(self, secret: str, timestamp: int | None = None) -> str:
        if timestamp is None:
            timestamp = int(time.time())
        counter = timestamp // self._step_seconds
        counter_bytes = struct.pack(">Q", counter)
        secret_decoded = base64.b32decode(secret.upper())
        hash_obj = hmac.new(secret_decoded, counter_bytes, hashlib.sha1).digest()
        offset = hash_obj[-1] & 0x0F
        truncated = struct.unpack(">I", hash_obj[offset:offset + 4])[0] & 0x7FFFFFFF
        code = truncated % 1_000_000
        return f"{code:06d}"

    def verify_totp(self, code: str, secret: str) -> bool:
        timestamp = int(time.time())
        for step in range(-self._drift_steps, self._drift_steps + 1):
            expected = self.generate_totp_code(secret, timestamp + step * self._step_seconds)
            if hmac.compare_digest(code, expected):
                return True
        return False

    def generate_recovery_codes(self, count: int = 10) -> list[str]:
        codes: list[str] = []
        for _ in range(count):
            code = secrets.token_hex(8)
            self._recovery_codes[code] = True
            codes.append(code)
        return codes

    def verify_recovery_code(self, code: str) -> bool:
        if code in self._recovery_codes and self._recovery_codes[code]:
            self._recovery_codes[code] = False
            return True
        return False

    async def authenticate(self, request: Any) -> dict[str, Any]:
        return {"authenticated": False, "method": "mfa", "error": "MFA requires interactive verification"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        return {"valid": False, "error": "MFA tokens not supported"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "drift_steps": self._drift_steps,
            "step_seconds": self._step_seconds,
            "recovery_codes_remaining": sum(1 for v in self._recovery_codes.values() if v),
        }
