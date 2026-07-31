"""
Code Editor Component
"""

from dataclasses import dataclass
from enum import Enum


class EditorLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    GO = "go"
    RUST = "rust"
    JAVA = "java"


class EditorTheme(Enum):
    DARK = "dark"
    LIGHT = "light"
    MONOKAI = "monokai"
    DRACULA = "dracula"


@dataclass
class Cursor:
    line: int = 0
    column: int = 0

    def move_up(self, lines=1):
        self.line = max(0, self.line - lines)

    def move_down(self, lines=1):
        self.line += lines

    def move_left(self, cols=1):
        self.column = max(0, self.column - cols)

    def move_right(self, cols=1):
        self.column += cols

    def goto_line(self, line):
        self.line = max(0, line)

    def goto_column(self, col):
        self.column = max(0, col)


@dataclass
class Selection:
    start_line: int = 0
    start_column: int = 0
    end_line: int = 0
    end_column: int = 0

    @property
    def is_empty(self):
        return self.start_line == self.end_line and self.start_column == self.end_column


@dataclass
class EditorConfig:
    tab_size: int = 4
    insert_spaces: bool = True
    word_wrap: bool = False
    line_numbers: bool = True
    minimap: bool = True
    auto_indent: bool = True
    bracket_matching: bool = True
    auto_close_brackets: bool = True
    highlight_active_line: bool = True
    font_size: int = 14
    font_family: str = "JetBrains Mono"
    auto_save: bool = True


@dataclass
class Completion:
    label: str
    kind: str = "text"
    detail: str | None = None
    insert_text: str = ""

    def __post_init__(self):
        if not self.insert_text:
            self.insert_text = self.label


@dataclass
class Diagnostic:
    line: int
    column: int
    message: str = ""
    severity: str = "error"
    source: str = ""


class CodeEditor:
    def __init__(self, config=None):
        self.config = config or EditorConfig()
        self.content = [""]
        self.cursor = Cursor()
        self.selection = Selection()
        self.language = EditorLanguage.PYTHON
        self.theme = EditorTheme.DARK
        self.history = [[]]
        self.history_index = 0
        self.diagnostics = []
        self.completions = []
        self.dirty = False
        self.filename = None
        self.listeners = {}

    def set_content(self, content):
        self.content = content.split("\n")
        self._record_history()
        self._emit("content_changed", {"content": content})

    def get_content(self):
        return "\n".join(self.content)

    def get_line(self, line):
        if 0 <= line < len(self.content):
            return self.content[line]
        return ""

    def insert_text(self, text):
        line = self.content[self.cursor.line]
        before = line[: self.cursor.column]
        after = line[self.cursor.column :]
        self.content[self.cursor.line] = before + text + after
        self.cursor.column += len(text)
        self._record_history()
        self.dirty = True
        self._emit("content_changed", {"content": self.get_content()})

    def delete_selection(self):
        if self.selection.is_empty:
            return
        start_line = self.selection.start_line
        start_col = self.selection.start_column
        end_line = self.selection.end_line
        end_col = self.selection.end_column
        before = self.content[start_line][:start_col]
        after = self.content[end_line][end_col:]
        self.content[start_line] = before + after
        del self.content[start_line + 1 : end_line + 1]
        self.cursor.line = start_line
        self.cursor.column = start_col
        self.selection = Selection()
        self._record_history()
        self.dirty = True

    def select_all(self):
        self.selection = Selection(
            start_line=0,
            start_column=0,
            end_line=len(self.content) - 1,
            end_column=len(self.content[-1]) if self.content else 0,
        )

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.content = self.history[self.history_index].copy()
            self._emit("content_changed", {"content": self.get_content()})

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.content = self.history[self.history_index].copy()
            self._emit("content_changed", {"content": self.get_content()})

    def _record_history(self):
        self.history = self.history[: self.history_index + 1]
        self.history.append(self.content.copy())
        self.history_index = len(self.history) - 1

    def format_document(self):
        self._emit("format_request", {"content": self.get_content()})

    def trigger_completion(self):
        line = self.get_line(self.cursor.line)
        prefix = line[: self.cursor.column]
        self._emit("completion_request", {"prefix": prefix, "line": self.cursor.line})

    def show_diagnostics(self, diagnostics):
        self.diagnostics = diagnostics
        self._emit("diagnostics_changed", {"diagnostics": diagnostics})

    def go_to_definition(self):
        self._emit("definition_request", {"line": self.cursor.line, "column": self.cursor.column})

    def find_references(self):
        self._emit("references_request", {"line": self.cursor.line, "column": self.cursor.column})

    def toggle_comment(self):
        line = self.get_line(self.cursor.line)
        if line.lstrip().startswith("#"):
            indent = len(line) - len(line.lstrip())
            self.content[self.cursor.line] = line[:indent] + line[indent + 2 :]
        else:
            indent = len(line) - len(line.lstrip())
            self.content[self.cursor.line] = line[:indent] + "# " + line[indent:]
        self._record_history()

    def indent_line(self):
        indent = " " * self.config.tab_size
        line = self.get_line(self.cursor.line)
        self.content[self.cursor.line] = indent + line
        self.cursor.column += self.config.tab_size
        self._record_history()

    def outdent_line(self):
        line = self.get_line(self.cursor.line)
        spaces = len(line) - len(line.lstrip())
        remove = min(spaces, self.config.tab_size)
        self.content[self.cursor.line] = line[remove:]
        self.cursor.column = max(0, self.cursor.column - remove)
        self._record_history()

    def duplicate_line(self):
        line = self.get_line(self.cursor.line)
        self.content.insert(self.cursor.line + 1, line)
        self.cursor.line += 1
        self._record_history()

    def move_line_up(self):
        if self.cursor.line > 0:
            line = self.content.pop(self.cursor.line)
            self.content.insert(self.cursor.line - 1, line)
            self.cursor.line -= 1
            self._record_history()

    def move_line_down(self):
        if self.cursor.line < len(self.content) - 1:
            line = self.content.pop(self.cursor.line)
            self.content.insert(self.cursor.line + 1, line)
            self.cursor.line += 1
            self._record_history()

    def find(self, query, case_sensitive=False):
        import re

        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        for i, line in enumerate(self.content):
            for match in re.finditer(re.escape(query), line, flags):
                results.append((i, match.start()))
        return results

    def replace_all(self, find, replace, case_sensitive=False):
        import re

        count = 0
        flags = 0 if case_sensitive else re.IGNORECASE
        for i, line in enumerate(self.content):
            new_line, n = re.subn(re.escape(find), replace, line, flags=flags)
            self.content[i] = new_line
            count += n
        if count > 0:
            self._record_history()
        return count

    def on(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def _emit(self, event, data):
        for callback in self.listeners.get(event, []):
            callback(data)
