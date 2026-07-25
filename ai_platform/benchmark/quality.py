from __future__ import annotations

import difflib

from ..providers.base_provider import ChatResponse


class QualityBenchmark:
    @staticmethod
    def evaluate_response(response: ChatResponse, expected: str) -> dict:
        content = ""
        if response.choices:
            content = response.choices[0].message.get("content", "")
        return QualityBenchmark.score(content, expected)

    @staticmethod
    def score(response: str, expected: str) -> dict:
        if not response or not expected:
            return {"score": 0.0, "exact_match": False, "similarity": 0.0, "length_ratio": 0.0}

        exact = response.strip() == expected.strip()
        similarity = difflib.SequenceMatcher(None, response.strip(), expected.strip()).ratio()

        len_ratio = len(response) / max(len(expected), 1)
        if len_ratio > 1.0:
            len_ratio = 1.0 / len_ratio

        weighted = similarity * 0.7 + len_ratio * 0.3
        score_val = 1.0 if exact else min(weighted, 1.0)

        return {
            "score": round(score_val, 4),
            "exact_match": exact,
            "similarity": round(similarity, 4),
            "length_ratio": round(len_ratio, 4),
        }

    @staticmethod
    def contains_key_points(response: str, key_points: list[str]) -> dict:
        results = {}
        matched = 0
        for point in key_points:
            found = point.lower() in response.lower()
            results[point] = found
            if found:
                matched += 1
        return {
            "matched": matched,
            "total": len(key_points),
            "coverage": round(matched / max(len(key_points), 1), 4),
            "details": results,
        }
