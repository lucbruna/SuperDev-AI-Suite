from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, field

from .conversation import Conversation, Message


TRUNCATION_STRATEGIES = {
    "trim_oldest": "trim_oldest",
    "trim_middle": "trim_middle",
    "summarize": "summarize",
}

TOKEN_ESTIMATE_PER_CHAR = 0.25


@dataclass
class ConversationHistory:
    conversation: Conversation
    max_tokens: int = 4096
    truncation_strategy: str = "trim_oldest"
    summarization_threshold: float = 0.8

    def estimate_tokens(self, text: str) -> int:
        return int(len(text) * TOKEN_ESTIMATE_PER_CHAR) + 1

    def total_tokens(self) -> int:
        total = 0
        for msg in self.conversation.messages:
            total += self.estimate_tokens(msg.content)
        return total

    def needs_truncation(self) -> bool:
        return self.total_tokens() > self.max_tokens * self.summarization_threshold

    def needs_summarization(self) -> bool:
        return self.total_tokens() > self.max_tokens

    def truncate(self) -> list[Message]:
        if not self.needs_truncation():
            return self.conversation.messages

        if self.truncation_strategy == "trim_oldest":
            while self.total_tokens() > self.max_tokens and len(self.conversation.messages) > 1:
                self.conversation.messages.pop(0)

        elif self.truncation_strategy == "trim_middle":
            if len(self.conversation.messages) > 2:
                keep_first = [self.conversation.messages[0]]
                keep_last = [self.conversation.messages[-1]]
                middle = self.conversation.messages[1:-1]
                while self.total_tokens_from_list(keep_first + middle + keep_last) > self.max_tokens and middle:
                    middle.pop(len(middle) // 2)
                self.conversation.messages = keep_first + middle + keep_last

        return self.conversation.messages

    @staticmethod
    def total_tokens_from_list(messages: list[Message]) -> int:
        return sum(int(len(m.content) * TOKEN_ESTIMATE_PER_CHAR) + 1 for m in messages)

    def get_context_messages(self, max_context_tokens: Optional[int] = None) -> list[Message]:
        limit = max_context_tokens or self.max_tokens
        result = []
        total = 0
        for msg in reversed(self.conversation.messages):
            tokens = self.estimate_tokens(msg.content)
            if total + tokens > limit:
                break
            result.insert(0, msg)
            total += tokens
        return result

    def to_dict_list(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.conversation.messages]
