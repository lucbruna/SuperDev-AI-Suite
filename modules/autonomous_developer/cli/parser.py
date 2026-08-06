"""Deterministic CLI argument parsing and dispatch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["ArgumentParser", "CLI", "CLIArgs", "CLIError", "CLIResult"]

DEFAULT_COMMANDS = ["plan", "run", "test", "review", "help"]
DEFAULT_VALUE_OPTIONS = ("config", "output", "name", "goal")


class CLIError(ValueError):
    """Raised for malformed or unknown command lines."""


@dataclass(slots=True)
class CLIArgs:
    """A parsed command line: command, options and positional targets."""

    command: str
    options: dict[str, Any] = field(default_factory=dict)
    targets: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CLIResult:
    """Outcome of dispatching a command line."""

    ok: bool
    message: str = ""
    args: CLIArgs | None = None


class ArgumentParser:
    """Parses ``superdev <command> [options] [targets...]``.

    Options declared in ``value_options`` (by raw name, e.g. ``config``)
    consume the following token as their value; every other ``--name`` is a
    boolean flag. Dashes in option names are converted to underscores.
    """

    def __init__(
        self,
        commands: list[str] | None = None,
        value_options: list[str] | tuple[str, ...] | None = None,
    ) -> None:
        self.commands = list(commands or DEFAULT_COMMANDS)
        self.value_options = set(
            value_options if value_options is not None else DEFAULT_VALUE_OPTIONS
        )

    def parse(self, argv: list[str]) -> CLIArgs:
        argv = list(argv)
        if not argv:
            raise CLIError("No command given; use 'help'")
        command = argv.pop(0)
        if command not in self.commands:
            raise CLIError(f"Unknown command: {command!r}")
        options: dict[str, Any] = {}
        targets: list[str] = []
        index = 0
        while index < len(argv):
            token = argv[index]
            if token.startswith("--"):
                raw = token[2:]
                name = raw.replace("-", "_")
                if raw in self.value_options:
                    if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
                        raise CLIError(f"Option {token!r} requires a value")
                    options[name] = argv[index + 1]
                    index += 2
                else:
                    options[name] = True
                    index += 1
            else:
                targets.append(token)
                index += 1
        return CLIArgs(command=command, options=options, targets=targets)

    def help_text(self) -> str:
        lines = [
            "usage: superdev <command> [options] [targets...]",
            "",
            "commands:",
        ]
        lines.extend(f"  {command}" for command in self.commands)
        return "\n".join(lines)


class CLI:
    """Dispatches parsed command lines into simple results."""

    def __init__(self, parser: ArgumentParser | None = None) -> None:
        self.parser = parser or ArgumentParser()

    def execute(self, argv: list[str], ctx: Any = None) -> CLIResult:
        try:
            args = self.parser.parse(argv)
        except CLIError as exc:
            return CLIResult(ok=False, message=str(exc))
        if args.command == "help":
            return CLIResult(ok=True, message=self.parser.help_text(), args=args)
        return CLIResult(ok=True, message=f"Executed command: {args.command}", args=args)
