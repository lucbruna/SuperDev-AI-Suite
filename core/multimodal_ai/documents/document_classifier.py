from __future__ import annotations

import uuid
from typing import Any, Optional

DOCUMENT_TYPES = ["INVOICE", "CONTRACT", "REPORT", "EMAIL", "SPECIFICATION", "MANUAL"]


class DocumentClassifier:
    def __init__(self) -> None:
        self._classification_history: list[dict[str, Any]] = []

    async def classify_document(self, document: dict[str, Any]) -> dict[str, Any]:
        doc_type = await self.get_document_type(document)
        confidence = await self.get_classification_confidence(document)
        doc_id = document.get("id", document.get("document_id", uuid.uuid4().hex))
        result: dict[str, Any] = {
            "document_id": doc_id,
            "document_type": doc_type,
            "confidence": confidence,
            "classifier": "DocumentClassifier",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
        self._classification_history.append(result)
        return result

    async def get_document_type(self, document: dict[str, Any]) -> str:
        hints = document.get("type", "").upper()
        if hints in DOCUMENT_TYPES:
            return hints
        name = document.get("name", document.get("path", "")).lower()
        if "invoice" in name or "inv" in name:
            return "INVOICE"
        if "contract" in name or "agreement" in name:
            return "CONTRACT"
        if "report" in name:
            return "REPORT"
        if "email" in name:
            return "EMAIL"
        if "spec" in name:
            return "SPECIFICATION"
        if "manual" in name:
            return "MANUAL"
        return "REPORT"

    async def extract_document_id(self, document: dict[str, Any]) -> str:
        return document.get("id", document.get("document_id", uuid.uuid4().hex))

    async def get_classification_confidence(self, document: dict[str, Any]) -> float:
        explicit = document.get("confidence")
        if explicit is not None:
            return float(explicit)
        doc_type = await self.get_document_type(document)
        confidence_map: dict[str, float] = {
            "INVOICE": 0.92,
            "CONTRACT": 0.88,
            "REPORT": 0.85,
            "EMAIL": 0.95,
            "SPECIFICATION": 0.80,
            "MANUAL": 0.78,
        }
        return confidence_map.get(doc_type, 0.5)
