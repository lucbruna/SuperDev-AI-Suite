"""Terminal commands — builtin command registry with aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class TerminalCommand:
    """A builtin command exposed by the internal terminal."""

    name: str
    description: str
    handler: Callable[..., str] | None = None
    aliases: list[str] = field(default_factory=list)


class TerminalCommands:
    """Registry of builtin terminal commands."""

    def __init__(self) -> None:
        self._commands: dict[str, TerminalCommand] = {}
        self._aliases: dict[str, str] = {}

    def register(self, command: TerminalCommand) -> None:
        self._commands[command.name] = command
        for alias in command.aliases:
            self._aliases[alias] = command.name

    def get(self, name: str) -> TerminalCommand | None:
        resolved = self._aliases.get(name, name)
        return self._commands.get(resolved)

    def list(self) -> list[TerminalCommand]:
        return sorted(self._commands.values(), key=lambda c: c.name)

    def names(self) -> list[str]:
        return [c.name for c in self.list()]


__all__ = ["TerminalCommand", "TerminalCommands"]
