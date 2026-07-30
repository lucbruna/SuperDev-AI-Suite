from __future__ import annotations

import logging
from typing import Any

from .code_models import CodeModule


class CodeRegistry:
    """Registry for code modules."""

    def __init__(self) -> None:
        self._modules: dict[str, CodeModule] = {}
        self._log = logging.getLogger("superdev.code.registry")

    def register(self, module: CodeModule) -> None:
        self._modules[module.id] = module
        self._log.debug("Registered module %s", module.name)

    def get(self, module_id: str) -> CodeModule | None:
        return self._modules.get(module_id)

    def list_all(self) -> list[CodeModule]:
        return list(self._modules.values())

    def unregister(self, module_id: str) -> None:
        self._modules.pop(module_id, None)
