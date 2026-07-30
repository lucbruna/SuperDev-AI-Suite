from __future__ import annotations

from typing import Any, Dict, List


class FeedbackSample:
    """A single feedback sample."""

    def __init__(self, query: str, response: Any, feedback: float):
        self._query = query
        self._response = response
        self._feedback = feedback

    @property
    def query(self) -> str:
        return self._query

    @property
    def response(self) -> Any:
        return self._response

    @property
    def feedback(self) -> float:
        return self._feedback

    def to_dict(self) -> Dict[str, Any]:
        return {"query": self._query, "response": self._response, "feedback": self._feedback}


class FeedbackLearning:
    """Learns from user feedback signals."""

    def __init__(self):
        self._samples: List[FeedbackSample] = []

    @property
    def sample_count(self) -> int:
        return len(self._samples)

    def record(self, query: str, response: Any, feedback: float) -> FeedbackSample:
        sample = FeedbackSample(query, response, feedback)
        self._samples.append(sample)
        return sample

    def positive_samples(self, threshold: float = 0.5) -> List[FeedbackSample]:
        return [s for s in self._samples if s.feedback >= threshold]

    def negative_samples(self, threshold: float = 0.5) -> List[FeedbackSample]:
        return [s for s in self._samples if s.feedback < threshold]

    def average_feedback(self) -> float:
        if not self._samples:
            return 0.0
        return sum(s.feedback for s in self._samples) / len(self._samples)

    def clear(self) -> None:
        self._samples.clear()
