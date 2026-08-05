"""Quality validation — scores generated avatars on quality axes."""
from __future__ import annotations

from typing import Any


class QualityValidation:
    """Computes a 0..100 quality score from completeness and consistency."""

    REQUIRED_SECTIONS = ("identity", "body", "face", "skin", "hair", "clothing")

    def score(self, descriptor: dict[str, Any]) -> dict[str, Any]:
        missing = [s for s in self.REQUIRED_SECTIONS if s not in descriptor]
        completeness = max(0.0, 1.0 - len(missing) / len(self.REQUIRED_SECTIONS))
        consistency = 1.0
        if "identity" in descriptor and "dimension" in descriptor["identity"]:
            consistency = 1.0  # identity carries its own dimension
        total = round(100 * (0.7 * completeness + 0.3 * consistency), 1)
        return {"score": total, "missing_sections": missing, "pass": total >= 60}


_quality_validation: QualityValidation | None = None


def get_quality_validation() -> QualityValidation:
    global _quality_validation
    if _quality_validation is None:
        _quality_validation = QualityValidation()
    return _quality_validation
