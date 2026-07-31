from __future__ import annotations

import logging
from typing import Any


class ArtifactSigner:
    """Signs artifacts and verifies signatures."""

    def __init__(self, key_id: str | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.artifact.signer")
        self._key_id = key_id

    def sign(self, artifact: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def verify(self, artifact: str, signature: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def generate_key(self) -> dict[str, Any]:
        raise NotImplementedError

    def export_public(self) -> str:
        raise NotImplementedError
