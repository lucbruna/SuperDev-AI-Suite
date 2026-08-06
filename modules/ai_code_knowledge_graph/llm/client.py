"""LLM client — optional provider with a deterministic offline fallback.

The knowledge module never hard-depends on an external LLM: when no provider
is configured the :class:`EchoLLM` answers deterministically, which keeps RAG
and agents testable offline. Real providers can be wired later behind the
same ``LLMClient`` interface.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class LLMClient:
    """Minimal LLM facade: ``complete(system, user) -> str | None``."""

    def __init__(self, *, provider: str = "", model: str = "", api_key: str = "") -> None:
        self.provider = provider or os.getenv("SUPERDEV_KG_LLM_PROVIDER", "").strip().lower()
        self.model = model or os.getenv("SUPERDEV_KG_LLM_MODEL", "").strip()
        self.api_key = api_key or os.getenv("SUPERDEV_KG_LLM_API_KEY", "").strip()
        if not self.provider:
            self.provider = "echo"

    @property
    def available(self) -> bool:
        return self.provider != "" and self.provider != "echo"

    def complete(self, system: str, user: str, **kwargs: Any) -> str | None:
        """Return a completion, or ``None`` when the provider is unusable."""
        if self.provider == "echo":
            return f"ECHO[{len(system)}:{len(user)}]"
        if not self.available or not self.api_key:
            return None
        try:
            return self._complete_external(system, user, **kwargs)
        except Exception as exc:  # noqa: BLE001 — providers fail for many reasons
            logger.warning("LLM completion failed: %s", exc)
            return None

    def _complete_external(self, system: str, user: str, **kwargs: Any) -> str:
        """Call a real provider (stub: no provider ships with the module)."""
        raise NotImplementedError(f"No provider backend for '{self.provider}'")
