"""
Terminal Component
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TerminalTheme(Enum):
    DARK = "dark"
    LIGHT = "light"
    MONOKAI = "monokai"
    DRACULA = "dracula"


@dataclass
class TerminalLine:
    content: str
    timestamp: datetime = None
    line_type: str = "output"
    exit_code: int | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TerminalConfig:
    theme: TerminalTheme = TerminalTheme.DARK
    font_size: int = 14
    font_family: str = "JetBrains Mono"
    cursor_style: str = "block"
    cursor_blink: bool = True
    scrollback: int = 10000


class Terminal:
    def __init__(self, config=None):
        self.config = config or TerminalConfig()
        self.lines = []
        self.history = []
        self.history_index = -1
        self.current_input = ""
        self.cwd = "/home/user"
        self.env = {"HOME": "/home/user", "USER": "user", "SHELL": "/bin/bash"}
        self.aliases = {}
        self.running = False
        self.listeners = []

    def execute(self, command):
        self.lines.append(TerminalLine(command, line_type="command"))
        if not command.strip():
            return TerminalLine("", exit_code=0)
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        if cmd in self.aliases:
            expanded = self.aliases[cmd]
            command = expanded + " " + " ".join(args)
            parts = command.split()
            cmd = parts[0]
            args = parts[1:]
        if cmd == "cd":
            return self._cmd_cd(args)
        elif cmd == "pwd":
            return self._cmd_pwd()
        elif cmd == "ls":
            return self._cmd_ls(args)
        elif cmd == "echo":
            return self._cmd_echo(args)
        elif cmd == "clear":
            return self._cmd_clear()
        elif cmd == "history":
            return self._cmd_history()
        elif cmd == "export":
            return self._cmd_export(args)
        elif cmd == "alias":
            return self._cmd_alias(args)
        else:
            return self._cmd_external(cmd, args)

    def _cmd_cd(self, args):
        if not args:
            self.cwd = self.env.get("HOME", "/")
        else:
            target = args[0]
            if target == "~":
                self.cwd = self.env.get("HOME", "/")
            elif target == "..":
                self.cwd = "/".join(self.cwd.split("/")[:-1]) or "/"
            elif target.startswith("/"):
                self.cwd = target
            else:
                self.cwd = self.cwd + "/" + target
        return TerminalLine("", exit_code=0)

    def _cmd_pwd(self):
        return TerminalLine(self.cwd, exit_code=0)

    def _cmd_ls(self, args):
        return TerminalLine("file1.py  file2.js  directory/", exit_code=0)

    def _cmd_echo(self, args):
        text = " ".join(args)
        for key, value in self.env.items():
            text = text.replace("$" + key, value)
        return TerminalLine(text, exit_code=0)

    def _cmd_clear(self):
        self.lines.clear()
        return TerminalLine("", exit_code=0)

    def _cmd_history(self):
        lines = []
        for i, h in enumerate(self.history, 1):
            lines.append("  " + str(i) + "  " + h)
        return TerminalLine("\n".join(lines), exit_code=0)

    def _cmd_export(self, args):
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                self.env[key] = value
        return TerminalLine("", exit_code=0)

    def _cmd_alias(self, args):
        for arg in args:
            if "=" in arg:
                name, value = arg.split("=", 1)
                self.aliases[name] = value.strip("'\"")
        return TerminalLine("", exit_code=0)

    def _cmd_external(self, cmd, args):
        return TerminalLine("Command executed: " + cmd, exit_code=0)

    def write(self, text):
        self.lines.append(TerminalLine(text, line_type="output"))

    def writeln(self, text):
        self.write(text + "\n")

    def write_error(self, text):
        self.lines.append(TerminalLine(text, line_type="error"))

    def clear(self):
        self.lines.clear()

    def reset(self):
        self.lines.clear()
        self.history.clear()
        self.history_index = -1
        self.cwd = "/home/user"

    def get_history_command(self, direction):
        if not self.history:
            return ""
        self.history_index += direction
        self.history_index = max(-1, min(self.history_index, len(self.history) - 1))
        if self.history_index == -1:
            return ""
        return self.history[self.history_index]

    def resize(self, cols, rows):
        self._emit("resize", {"cols": cols, "rows": rows})

    def on(self, event, callback):
        self.listeners.append({"event": event, "callback": callback})

    def _emit(self, event, data):
        for listener in self.listeners:
            if listener["event"] == event:
                listener["callback"](data)
