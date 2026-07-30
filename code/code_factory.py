from __future__ import annotations

from .code_config import CodeConfig
from .code_engine import CodeEngine


class CodeFactory:
    """Factory for creating Code Engine instances."""

    @staticmethod
    def create_default() -> CodeEngine:
        return CodeEngine(config=CodeConfig())

    @staticmethod
    def create_with_config(config: CodeConfig) -> CodeEngine:
        return CodeEngine(config=config)
