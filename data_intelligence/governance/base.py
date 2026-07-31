"""Base classes for data governance."""

from __future__ import annotations

from dataclasses import dataclass, field

from data_intelligence.data_models import DataClassification


class GovernanceError(Exception):
    """Raised when a governance operation is invalid."""


@dataclass
class PolicyRule:
    """An access policy over a dataset.

    * ``action`` is one of ``allow`` / ``deny`` / ``review``.
    * ``max_classification`` (optional) caps the allowed classification.
    """

    dataset: str
    action: str = "allow"
    operation: str = "*"
    max_classification: DataClassification | None = None


CLASSIFICATION_LEVELS = {
    DataClassification.PUBLIC: 0,
    DataClassification.INTERNAL: 1,
    DataClassification.CONFIDENTIAL: 2,
    DataClassification.RESTRICTED: 3,
}
