"""LLM-specific exceptions shared by client and providers."""
from __future__ import annotations

from modules.autonomous_developer.core.exceptions import ExecutionError

__all__ = ["LLMError"]


class LLMError(ExecutionError):
    """Raised when no LLM provider can produce a completion."""
