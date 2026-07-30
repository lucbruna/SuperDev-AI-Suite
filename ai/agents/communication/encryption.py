from __future__ import annotations

import hashlib
from typing import Any, Dict


class Encryption:
    """Basic message encryption utilities."""

    @staticmethod
    def hash_content(content: Dict[str, Any]) -> str:
        raw = str(sorted(content.items()))
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def obfuscate(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {"method": "sha256"}
