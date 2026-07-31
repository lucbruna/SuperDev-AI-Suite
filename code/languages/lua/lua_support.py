from __future__ import annotations

import logging


class LuaSupport:
    """Lua language support utilities."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages.lua")

    @property
    def extensions(self) -> list[str]:
        return [".lua"]

    def is_lua_file(self, path: str) -> bool:
        return path.endswith(".lua")
