from __future__ import annotations

from typing import Any


class VectorValidator:
    """Validate vector data integrity and constraints."""

    @staticmethod
    def validate_vector(vector: list[float], expected_dim: int | None = None, allow_empty: bool = False) -> dict[str, Any]:
        errors: list[str] = []
        if not vector:
            if not allow_empty:
                errors.append("Vector is empty")
        else:
            if expected_dim is not None and len(vector) != expected_dim:
                errors.append(f"Expected dimension {expected_dim}, got {len(vector)}")
            for i, v in enumerate(vector):
                if not isinstance(v, (int, float)):
                    errors.append(f"Value at index {i} is not numeric: {type(v).__name__}")
        return {"valid": len(errors) == 0, "errors": errors, "dimension": len(vector)}

    @staticmethod
    def validate_vectors(vectors: list[list[float]]) -> dict[str, Any]:
        if not vectors:
            return {"valid": False, "errors": ["Empty collection"], "count": 0}
        dim = len(vectors[0])
        errors: list[str] = []
        for i, vec in enumerate(vectors):
            result = VectorValidator.validate_vector(vec, expected_dim=dim)
            if not result["valid"]:
                errors.append(f"Vector at index {i}: {result['errors']}")
        return {"valid": len(errors) == 0, "errors": errors, "count": len(vectors), "dimension": dim}

    @staticmethod
    def validate_metadata(metadata: dict[str, Any], required_keys: list[str] | None = None) -> dict[str, Any]:
        errors: list[str] = []
        if required_keys:
            for key in required_keys:
                if key not in metadata:
                    errors.append(f"Missing required key: {key}")
        return {"valid": len(errors) == 0, "errors": errors}
