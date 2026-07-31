"""
Dead Letter Queue - Unprocessable messages
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DeadLetter:
    letter_id: str
    original_queue: str
    message_id: str
    payload: Any = None
    error: str = ""
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    reviewed: bool = False


class DeadLetterQueue:
    def __init__(self):
        self.letters: dict[str, DeadLetter] = {}
        self.reviewers: list[str] = []

    def add(
        self, original_queue: str, message_id: str, payload: Any = None, error: str = "", attempts: int = 0
    ) -> DeadLetter:
        letter_id = hashlib.sha256(f"{message_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        letter = DeadLetter(
            letter_id=letter_id,
            original_queue=original_queue,
            message_id=message_id,
            payload=payload,
            error=error,
            attempts=attempts,
        )
        self.letters[letter_id] = letter
        return letter

    def review(self, letter_id: str, reviewer: str = "") -> bool:
        letter = self.letters.get(letter_id)
        if letter:
            letter.reviewed = True
            if reviewer:
                self.reviewers.append(reviewer)
            return True
        return False

    def requeue(self, letter_id: str) -> DeadLetter | None:
        letter = self.letters.get(letter_id)
        if letter:
            letter.reviewed = True
            return letter
        return None

    def get_unreviewed(self) -> list[DeadLetter]:
        return [l for l in self.letters.values() if not l.reviewed]

    def get_letter(self, letter_id: str) -> DeadLetter | None:
        return self.letters.get(letter_id)

    def list_all(self) -> list[DeadLetter]:
        return list(self.letters.values())

    def count(self) -> int:
        return len(self.letters)
