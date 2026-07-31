from __future__ import annotations

import hashlib
from typing import Any


class Encryption:
    """Basic message encryption utilities."""

    @staticmethod
    def hash_content(content: dict[str, Any]) -> str:
        raw = str(sorted(content.items()))
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def obfuscate(text: str) -> str:
        # sha256 instead of md5 — obfuscation must not rely on a broken hash.
        return hashlib.sha256(text.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {"method": "sha256"}
