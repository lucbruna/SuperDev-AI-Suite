"""
AI Code Assistant
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AssistantMode(Enum):
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: float = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    is_streaming: bool = False


@dataclass
class AssistantContext:
    file_path: str | None = None
    file_content: str | None = None
    selection: str | None = None
    cursor_line: int = 0
    cursor_column: int = 0
    language: str = "python"
    project_files: list[str] = field(default_factory=list)


@dataclass
class CodeBlock:
    language: str
    code: str
    filename: str | None = None
    line_start: int = 0

    @property
    def is_complete(self):
        return bool(self.code.strip())


class AIAssistant:
    def __init__(self):
        self.messages = []
        self.context = AssistantContext()
        self.mode = AssistantMode.CHAT
        self.is_streaming = False
        self.listeners = []
        self.conversation_id = None
        self.system_prompt = "You are SuperDev AI Assistant, an expert coding assistant."

    def send_message(self, content):
        message = Message(role=MessageRole.USER, content=content)
        self.messages.append(message)
        self._emit("message_sent", {"message": message})
        return message

    def receive_message(self, content, is_streaming=False):
        message = Message(role=MessageRole.ASSISTANT, content=content, is_streaming=is_streaming)
        self.messages.append(message)
        self._emit("message_received", {"message": message})
        return message

    def generate_code(self, prompt, language="python"):
        self.context.language = language
        enhanced_prompt = "Generate " + language + " code: " + prompt
        self.send_message(enhanced_prompt)
        generated = "# Generated code\n# " + prompt + "\n\ndef solution():\n    pass"
        self.receive_message(generated)
        return generated

    def explain_code(self, code, language="python"):
        self.context.file_content = code
        self.context.language = language
        prompt = "Explain this " + language + " code:\n\n```" + language + "\n" + code + "\n```"
        self.send_message(prompt)
        explanation = "This code..."
        self.receive_message(explanation)
        return explanation

    def review_code(self, code, language="python"):
        self.context.file_content = code
        self.context.language = language
        prompt = "Review this " + language + " code:\n\n```" + language + "\n" + code + "\n```"
        self.send_message(prompt)
        reviews = [{"type": "info", "message": "Code looks good"}]
        self.receive_message(json.dumps(reviews))
        return reviews

    def refactor_code(self, code, instruction=""):
        prompt = "Refactor this code: " + instruction + "\n\n```\n" + code + "\n```"
        self.send_message(prompt)
        refactored = code
        self.receive_message(refactored)
        return refactored

    def debug_code(self, code, error=""):
        prompt = "Debug this code. Error: " + error + "\n\n```\n" + code + "\n```"
        self.send_message(prompt)
        suggestion = "Check for..."
        self.receive_message(suggestion)
        return suggestion

    def generate_documentation(self, code, language="python"):
        prompt = "Generate documentation for this " + language + " code:\n\n```" + language + "\n" + code + "\n```"
        self.send_message(prompt)
        docs = """Module documentation."""
        self.receive_message(docs)
        return docs

    def update_context(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)

    def clear_conversation(self):
        self.messages.clear()
        self.conversation_id = None
        self._emit("conversation_cleared", {})

    def extract_code_blocks(self, text):
        blocks = []
        in_block = False
        current_lang = ""
        current_code = []
        for line in text.split("\n"):
            if line.startswith("```") and not in_block:
                in_block = True
                current_lang = line[3:].strip()
                current_code = []
            elif line.startswith("```") and in_block:
                in_block = False
                blocks.append(CodeBlock(language=current_lang, code="\n".join(current_code)))
            elif in_block:
                current_code.append(line)
        return blocks

    def on(self, event, callback):
        self.listeners.append({"event": event, "callback": callback})

    def _emit(self, event, data):
        for listener in self.listeners:
            if listener["event"] == event:
                listener["callback"](data)
