from __future__ import annotations

from typing import Any, Dict, List, Optional

from .builder import ContextBuilder
from .compressor import ContextCompressor
from .expander import ContextExpander
from .filter import ContextFilter
from .loader import ContextLoader
from .optimizer import ContextOptimizer
from .ranker import ContextRanker
from .router import ContextRouter
from .validator import ContextValidator
from .window import ContextWindow


class ContextManager:
    """Facade for the context subsystem — build, manage, and query context."""

    def __init__(self):
        self._builder = ContextBuilder()
        self._loader = ContextLoader()
        self._optimizer = ContextOptimizer()
        self._validator = ContextValidator()
        self._window = ContextWindow()
        self._compressor = ContextCompressor()
        self._expander = ContextExpander()
        self._ranker = ContextRanker()
        self._filter = ContextFilter()
        self._router = ContextRouter()
        self._contexts: Dict[str, Any] = {}

    @property
    def builder(self) -> ContextBuilder:
        return self._builder

    @property
    def loader(self) -> ContextLoader:
        return self._loader

    @property
    def optimizer(self) -> ContextOptimizer:
        return self._optimizer

    @property
    def validator(self) -> ContextValidator:
        return self._validator

    @property
    def window(self) -> ContextWindow:
        return self._window

    @property
    def compressor(self) -> ContextCompressor:
        return self._compressor

    @property
    def expander(self) -> ContextExpander:
        return self._expander

    @property
    def ranker(self) -> ContextRanker:
        return self._ranker

    @property
    def filter(self) -> ContextFilter:
        return self._filter

    @property
    def router(self) -> ContextRouter:
        return self._router

    def build_context(self, name: str, sources: List[str]) -> Dict[str, Any]:
        ctx = self._builder.build(sources)
        self._contexts[name] = ctx
        return ctx

    def get_context(self, name: str) -> Optional[Any]:
        return self._contexts.get(name)

    def list_contexts(self) -> List[str]:
        return list(self._contexts.keys())

    def remove_context(self, name: str) -> bool:
        return self._contexts.pop(name, None) is not None

    def clear(self) -> None:
        self._contexts.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "context_count": len(self._contexts),
            "context_names": list(self._contexts.keys()),
        }
