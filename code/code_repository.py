from __future__ import annotations

import logging

from .code_models import CodeModule


class CodeRepository:
    """Persistence layer for code modules."""

    def __init__(self) -> None:
        self._modules: dict[str, CodeModule] = {}
        self._log = logging.getLogger("superdev.code.repository")

    def save(self, module: CodeModule) -> None:
        self._modules[module.id] = module
        self._log.debug("Saved module %s", module.name)

    def get(self, module_id: str) -> CodeModule | None:
        return self._modules.get(module_id)

    def delete(self, module_id: str) -> None:
        self._modules.pop(module_id, None)
