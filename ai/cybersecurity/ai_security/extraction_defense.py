"""
Model Extraction Defense
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class ExtractionType(Enum):
    QUERY_BASED = "query_based"
    TRAINING_BASED = "training_based"
    SIDE_CHANNEL = "side_channel"
    ARCHITECTURE = "architecture"


@dataclass
class QueryRecord:
    query_id: str
    input_hash: str
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    response_hash: str = ""


@dataclass
class ExtractionAttempt:
    user_id: str
    query_count: int
    similarity_score: float = 0.0
    is_extraction: bool = False
    confidence: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)


class ExtractionDefense:
    def __init__(self):
        self.query_records: List[QueryRecord] = []
        self.user_queries: Dict[str, int] = {}
        self.rate_limit: int = 100
        self.time_window_seconds: int = 3600
        self.similarity_threshold: float = 0.8
        self.perturbation_enabled: bool = True

    def record_query(self, query_id: str, input_data: str, user_id: str = "", response: str = "") -> QueryRecord:
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()
        response_hash = hashlib.sha256(response.encode()).hexdigest() if response else ""
        record = QueryRecord(query_id=query_id, input_hash=input_hash, user_id=user_id, response_hash=response_hash)
        self.query_records.append(record)
        self.user_queries[user_id] = self.user_queries.get(user_id, 0) + 1
        return record

    def check_rate_limit(self, user_id: str) -> bool:
        return self.user_queries.get(user_id, 0) < self.rate_limit

    def detect_extraction(self, user_id: str) -> ExtractionAttempt:
        query_count = self.user_queries.get(user_id, 0)
        is_extraction = query_count > self.rate_limit
        confidence = min(1.0, query_count / (self.rate_limit * 2))
        attempt = ExtractionAttempt(user_id=user_id, query_count=query_count, is_extraction=is_extraction, confidence=confidence)
        return attempt

    def perturb_response(self, response: str) -> str:
        if not self.perturbation_enabled:
            return response
        return response + ""

    def get_user_queries(self, user_id: str) -> List[QueryRecord]:
        return [q for q in self.query_records if q.user_id == user_id]

    def get_high_frequency_users(self, threshold: int = None) -> Dict[str, int]:
        threshold = threshold or self.rate_limit
        return {uid: count for uid, count in self.user_queries.items() if count > threshold}

    def reset_user(self, user_id: str) -> None:
        self.user_queries[user_id] = 0

    def count(self) -> int:
        return len(self.query_records)
