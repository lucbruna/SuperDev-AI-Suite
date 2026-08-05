"""Voice Similarity — compares voice embeddings with cosine distance."""
from __future__ import annotations

import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity in [0, 1] (1 = identical)."""
    na = np.linalg.norm(a) + 1e-9
    nb = np.linalg.norm(b) + 1e-9
    return float(np.dot(a, b) / (na * nb))


def similarity_score(a: np.ndarray, b: np.ndarray) -> float:
    """0-100 voice similarity score (matching human 'same speaker' intuition)."""
    cos = cosine_similarity(a, b)
    return round(max(0.0, min(1.0, cos)) * 100.0, 1)


def match_threshold() -> float:
    """Similarity above this is considered the same speaker."""
    return 0.88
