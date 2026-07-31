"""Face - Face recognition module."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class FaceTemplate:
    template_id: str
    user_id: str
    embedding: list[float] = field(default_factory=list)
    quality: float = 0.0
    liveness_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True


class FaceRecognitionManager:
    def __init__(self):
        self.templates: dict[str, FaceTemplate] = {}
        self.recognition_log: list[dict[str, Any]] = []

    def enroll(self, user_id: str, embedding: list[float] = None, quality: float = 0.0) -> FaceTemplate:
        template_id = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        template = FaceTemplate(template_id=template_id, user_id=user_id, embedding=embedding or [], quality=quality)
        self.templates[template_id] = template
        return template

    def recognize(self, probe_embedding: list[float] = None, threshold: float = 0.8) -> str | None:
        best_match = None
        best_score = 0.0
        for t in self.templates.values():
            if not t.active or not t.embedding or not probe_embedding:
                continue
            score = sum(a * b for a, b in zip(t.embedding, probe_embedding, strict=False)) / (sum(a ** 2 for a in t.embedding) ** 0.5 * sum(b ** 2 for b in probe_embedding) ** 0.5) if probe_embedding else 0
            if score > best_score and score >= threshold:
                best_score = score
                best_match = t.user_id
        self.recognition_log.append({"match": best_match, "score": best_score, "timestamp": datetime.now().isoformat()})
        return best_match

    def verify(self, user_id: str, probe_embedding: list[float] = None) -> bool:
        for t in self.templates.values():
            if t.user_id == user_id and t.active and t.embedding and probe_embedding:
                score = sum(a * b for a, b in zip(t.embedding, probe_embedding, strict=False)) / (sum(a ** 2 for a in t.embedding) ** 0.5 * sum(b ** 2 for b in probe_embedding) ** 0.5) if probe_embedding else 0
                return score >= 0.8
        return False

    def get_user_templates(self, user_id: str) -> list[FaceTemplate]:
        return [t for t in self.templates.values() if t.user_id == user_id and t.active]

    def remove(self, template_id: str) -> bool:
        if template_id in self.templates:
            self.templates[template_id].active = False
            return True
        return False

    def count(self) -> int:
        return len([t for t in self.templates.values() if t.active])
