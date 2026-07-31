"""
Dead Letter Queue - Unprocessable messages
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


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
        self.letters: Dict[str, DeadLetter] = {}
        self.reviewers: List[str] = []

    def add(self, original_queue: str, message_id: str, payload: Any = None, error: str = "", attempts: int = 0) -> DeadLetter:
        letter_id = hashlib.sha256(f"{message_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        letter = DeadLetter(letter_id=letter_id, original_queue=original_queue, message_id=message_id, payload=payload, error=error, attempts=attempts)
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

    def requeue(self, letter_id: str) -> Optional[DeadLetter]:
        letter = self.letters.get(letter_id)
        if letter:
            letter.reviewed = True
            return letter
        return None

    def get_unreviewed(self) -> List[DeadLetter]:
        return [l for l in self.letters.values() if not l.reviewed]

    def get_letter(self, letter_id: str) -> Optional[DeadLetter]:
        return self.letters.get(letter_id)

    def list_all(self) -> List[DeadLetter]:
        return list(self.letters.values())

    def count(self) -> int:
        return len(self.letters)
