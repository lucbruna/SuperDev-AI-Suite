from __future__ import annotations

import re
from typing import Any

ENTITY_PATTERNS: dict[str, str] = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "url": r"https?://[^\s<>\"']+|www\.[^\s<>\"']+",
    "phone": r"\+?\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,4}",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "currency": r"\$\d+(?:,\d{3})*(?:\.\d{2})?|€\d+(?:,\d{3})*(?:\.\d{2})?|£\d+(?:,\d{3})*(?:\.\d{2})?",
}


class InformationExtractor:
    async def extract_entities(self, text: str) -> dict[str, list[str]]:
        entities: dict[str, list[str]] = {}
        for entity_type, pattern in ENTITY_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))
        return entities

    async def extract_dates(self, text: str) -> list[str]:
        patterns = [
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b\d{2}/\d{2}/\d{4}\b",
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
            r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b",
        ]
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text))
        return list(set(dates))

    async def extract_values(self, text: str, value_type: str = "numeric") -> list[str]:
        patterns = {
            "numeric": r"\b\d+(?:\.\d+)?\b",
            "percentage": r"\b\d+(?:\.\d+)?%",
            "measurement": r"\b\d+(?:\.\d+)?\s*(?:km|m|cm|mm|kg|g|l|ml|px|em|rem)\b",
        }
        pattern = patterns.get(value_type)
        if pattern is None:
            raise ValueError(f"Unknown value type: '{value_type}'. Supported: {', '.join(patterns)}")
        return list(set(re.findall(pattern, text, re.IGNORECASE)))

    async def extract_relationships(self, text: str) -> list[dict[str, str]]:
        patterns = [
            (r"(\w+)\s+is a\s+(\w+)", "is_a"),
            (r"(\w+)\s+(?:belongs to|part of)\s+(\w+)", "part_of"),
            (r"(\w+)\s+(?:depends on|requires)\s+(\w+)", "depends_on"),
            (r"(\w+)\s+(?:leads to|causes|produces)\s+(\w+)", "causes"),
        ]
        relationships = []
        for pattern, rel_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                relationships.append({
                    "subject": match.group(1),
                    "predicate": rel_type,
                    "object": match.group(2),
                })
        return relationships

    async def extract_tables(self, text: str) -> list[dict[str, Any]]:
        tables = []
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "|" in line and line.count("|") >= 3:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2:
                    tables.append({
                        "row": len(tables) + 1,
                        "line": i + 1,
                        "cells": cells,
                        "column_count": len(cells),
                    })
        if not tables:
            tables = [{"row": 1, "line": 1, "cells": ["no tables found"], "column_count": 1}]
        return tables