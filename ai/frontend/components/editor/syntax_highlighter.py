"""
Syntax Highlighting Engine
"""

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    KEYWORD = "keyword"
    STRING = "string"
    NUMBER = "number"
    COMMENT = "comment"
    FUNCTION = "function"
    VARIABLE = "variable"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    TYPE = "type"
    CONSTANT = "constant"
    TEXT = "text"


@dataclass
class Token:
    type: TokenType
    value: str
    start: int
    end: int
    line: int = 0
    column: int = 0

    @property
    def length(self):
        return self.end - self.start


@dataclass
class LanguageGrammar:
    name: str
    keywords: list[str]
    builtins: list[str]
    constants: list[str]
    single_line_comment: str = "//"
    string_delimiters: list[str] = None

    def __post_init__(self):
        if self.string_delimiters is None:
            self.string_delimiters = ['"', "'"]


class SyntaxHighlighter:
    GRAMMARS = {
        "python": LanguageGrammar(
            name="python",
            keywords=[
                "def",
                "class",
                "if",
                "else",
                "elif",
                "for",
                "while",
                "return",
                "import",
                "from",
                "as",
                "try",
                "except",
                "finally",
                "with",
                "yield",
                "lambda",
                "pass",
                "break",
                "continue",
                "and",
                "or",
                "not",
                "in",
                "is",
                "True",
                "False",
                "None",
                "self",
            ],
            builtins=[
                "print",
                "len",
                "range",
                "int",
                "str",
                "float",
                "list",
                "dict",
                "set",
                "tuple",
                "type",
                "isinstance",
                "hasattr",
            ],
            constants=["True", "False", "None"],
            single_line_comment="#",
            string_delimiters=['"', "'"],
        ),
        "javascript": LanguageGrammar(
            name="javascript",
            keywords=[
                "function",
                "const",
                "let",
                "var",
                "if",
                "else",
                "for",
                "while",
                "return",
                "class",
                "extends",
                "import",
                "export",
                "async",
                "await",
                "try",
                "catch",
                "finally",
                "throw",
                "new",
                "this",
                "typeof",
                "instanceof",
            ],
            builtins=[
                "console",
                "Math",
                "JSON",
                "Object",
                "Array",
                "String",
                "Number",
                "Boolean",
                "Date",
                "Promise",
                "Map",
                "Set",
            ],
            constants=["true", "false", "null", "undefined"],
        ),
        "typescript": LanguageGrammar(
            name="typescript",
            keywords=[
                "function",
                "const",
                "let",
                "var",
                "if",
                "else",
                "for",
                "while",
                "return",
                "class",
                "extends",
                "import",
                "export",
                "interface",
                "type",
                "enum",
                "implements",
                "abstract",
                "public",
                "private",
                "protected",
                "readonly",
                "static",
            ],
            builtins=[
                "console",
                "Math",
                "JSON",
                "Object",
                "Array",
                "String",
                "Number",
                "Boolean",
                "Date",
                "Promise",
                "Map",
                "Set",
            ],
            constants=["true", "false", "null", "undefined"],
        ),
        "go": LanguageGrammar(
            name="go",
            keywords=[
                "func",
                "package",
                "import",
                "var",
                "const",
                "type",
                "struct",
                "interface",
                "if",
                "else",
                "for",
                "range",
                "return",
                "break",
                "continue",
                "switch",
                "case",
                "default",
                "select",
                "chan",
                "go",
                "defer",
                "map",
                "make",
                "new",
                "append",
                "len",
                "cap",
            ],
            builtins=["fmt", "strings", "math", "os", "io", "net", "http", "json", "time", "context", "errors", "log"],
            constants=["true", "false", "nil", "iota"],
            single_line_comment="//",
        ),
        "rust": LanguageGrammar(
            name="rust",
            keywords=[
                "fn",
                "let",
                "mut",
                "const",
                "struct",
                "enum",
                "impl",
                "trait",
                "pub",
                "use",
                "mod",
                "crate",
                "self",
                "super",
                "if",
                "else",
                "for",
                "while",
                "loop",
                "match",
                "return",
                "break",
                "continue",
                "move",
                "ref",
                "async",
                "await",
                "unsafe",
                "dyn",
                "where",
                "type",
                "static",
                "extern",
            ],
            builtins=[
                "println!",
                "format!",
                "vec!",
                "String",
                "Vec",
                "Option",
                "Result",
                "Box",
                "Rc",
                "Arc",
                "Mutex",
                "HashMap",
                "HashSet",
            ],
            constants=["true", "false", "Self"],
            single_line_comment="//",
        ),
        "java": LanguageGrammar(
            name="java",
            keywords=[
                "public",
                "private",
                "protected",
                "class",
                "interface",
                "enum",
                "extends",
                "implements",
                "abstract",
                "static",
                "final",
                "void",
                "int",
                "long",
                "double",
                "float",
                "boolean",
                "char",
                "byte",
                "short",
                "String",
                "if",
                "else",
                "for",
                "while",
                "do",
                "switch",
                "case",
                "break",
                "continue",
                "return",
                "try",
                "catch",
                "finally",
                "throw",
                "throws",
                "new",
                "this",
                "super",
                "instanceof",
                "import",
                "package",
            ],
            builtins=[
                "System",
                "String",
                "Integer",
                "Double",
                "Boolean",
                "List",
                "Map",
                "Set",
                "ArrayList",
                "HashMap",
                "HashSet",
                "Arrays",
                "Collections",
                "Objects",
                "Math",
                "Thread",
                "Exception",
            ],
            constants=["true", "false", "null"],
            single_line_comment="//",
        ),
    }

    def __init__(self):
        self.current_language = "python"
        self.tokens = []

    def highlight(self, code, language):
        self.current_language = language
        self.tokens = []
        grammar = self.GRAMMARS.get(language)
        if not grammar:
            return [Token(TokenType.TEXT, code, 0, len(code))]
        lines = code.split("\n")
        offset = 0
        for line_num, line in enumerate(lines):
            self._tokenize_line(line, line_num, offset, grammar)
            offset += len(line) + 1
        return self.tokens

    def _tokenize_line(self, line, line_num, offset, grammar):
        i = 0
        while i < len(line):
            if line[i : i + len(grammar.single_line_comment)] == grammar.single_line_comment:
                self.tokens.append(Token(TokenType.COMMENT, line[i:], offset + i, offset + len(line), line_num, i))
                break
            if line[i] in grammar.string_delimiters:
                delim = line[i]
                end = line.find(delim, i + 1)
                if end == -1:
                    end = len(line)
                else:
                    end += len(delim)
                self.tokens.append(Token(TokenType.STRING, line[i:end], offset + i, offset + end, line_num, i))
                i = end
                continue
            if line[i].isdigit():
                start = i
                while i < len(line) and (line[i].isdigit() or line[i] == "."):
                    i += 1
                self.tokens.append(Token(TokenType.NUMBER, line[start:i], offset + start, offset + i, line_num, start))
                continue
            if line[i].isalpha() or line[i] == "_":
                start = i
                while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                    i += 1
                word = line[start:i]
                if word in grammar.keywords:
                    token_type = TokenType.KEYWORD
                elif word in grammar.builtins or word in grammar.constants:
                    token_type = TokenType.CONSTANT
                elif i < len(line) and line[i] == "(":
                    token_type = TokenType.FUNCTION
                else:
                    token_type = TokenType.VARIABLE
                self.tokens.append(Token(token_type, word, offset + start, offset + i, line_num, start))
                continue
            if line[i] in "+-*/%=<>!&|^~?:.":
                self.tokens.append(Token(TokenType.OPERATOR, line[i], offset + i, offset + i + 1, line_num, i))
            elif line[i] in "(){}[];,@":
                self.tokens.append(Token(TokenType.PUNCTUATION, line[i], offset + i, offset + i + 1, line_num, i))
            else:
                self.tokens.append(Token(TokenType.TEXT, line[i], offset + i, offset + i + 1, line_num, i))
            i += 1

    def get_token_at(self, position):
        for token in self.tokens:
            if token.start <= position < token.end:
                return token
        return None

    def clear(self):
        self.tokens.clear()
