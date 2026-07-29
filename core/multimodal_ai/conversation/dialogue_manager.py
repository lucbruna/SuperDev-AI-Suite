from __future__ import annotations

import enum
from typing import Any, Optional


class DialogueState(enum.Enum):
    GREETING = "greeting"
    QUESTION = "question"
    COMMAND = "command"
    CLARIFICATION = "clarification"
    RESPONSE = "response"
    FAREWELL = "farewell"


GREETING_KEYWORDS = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]
QUESTION_KEYWORDS = ["what", "why", "how", "when", "where", "who", "which", "?"]
COMMAND_KEYWORDS = ["run", "execute", "do", "create", "make", "generate", "show"]
CLARIFICATION_KEYWORDS = ["mean", "clarify", "explain", "unsure", "confused"]
FAREWELL_KEYWORDS = ["bye", "goodbye", "exit", "quit", "end", "farewell"]


class DialogueManager:
    def __init__(self) -> None:
        self._turns: dict[str, int] = {}
        self._states: dict[str, DialogueState] = {}
        self._histories: dict[str, list[dict[str, Any]]] = {}

    def manage_dialogue(self, message: str) -> dict[str, Any]:
        state = self.decide_response_type(message)
        next_action = self.get_next_action(state)
        return {
            "state": state,
            "next_action": next_action,
            "response_type": state.value,
        }

    def get_next_action(self, state: DialogueState) -> str:
        actions = {
            DialogueState.GREETING: "greet_user",
            DialogueState.QUESTION: "answer_question",
            DialogueState.COMMAND: "execute_command",
            DialogueState.CLARIFICATION: "ask_clarification",
            DialogueState.RESPONSE: "generate_response",
            DialogueState.FAREWELL: "end_conversation",
        }
        return actions.get(state, "generate_response")

    def decide_response_type(self, message: str) -> DialogueState:
        lower = message.lower().strip()

        if lower in FAREWELL_KEYWORDS:
            return DialogueState.FAREWELL

        if lower in GREETING_KEYWORDS or lower.split()[0] in GREETING_KEYWORDS:
            return DialogueState.GREETING

        if any(kw in lower.split() for kw in CLARIFICATION_KEYWORDS):
            return DialogueState.CLARIFICATION

        if any(kw in lower.split() for kw in COMMAND_KEYWORDS):
            return DialogueState.COMMAND

        if any(kw in lower for kw in QUESTION_KEYWORDS):
            return DialogueState.QUESTION

        return DialogueState.RESPONSE

    def handle_turn(self, conversation_id: str, message: str, forced_state: Optional[str] = None) -> int:
        self._turns[conversation_id] = self._turns.get(conversation_id, 0) + 1
        state = DialogueState(forced_state) if forced_state else self.decide_response_type(message)
        self._states[conversation_id] = state
        if conversation_id not in self._histories:
            self._histories[conversation_id] = []
        self._histories[conversation_id].append(
            {"turn": self._turns[conversation_id], "message": message, "state": state.value}
        )
        return self._turns[conversation_id]

    def detect_dialogue_end(self, message: str) -> bool:
        return self.decide_response_type(message) == DialogueState.FAREWELL
