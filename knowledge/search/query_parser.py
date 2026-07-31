from __future__ import annotations

import logging


class QueryParser:
    """Parses and normalizes search queries, extracting keywords and filters."""

    def __init__(self, strip_filters: bool = True) -> None:
        self._log = logging.getLogger("superdev.knowledge.search.query_parser")
        self._strip_filters = strip_filters

    def keywords(self, query: str) -> list[str]:
        tokens = query.lower().split()
        return [token for token in tokens if token]

    def filters(self, query: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for token in query.split():
            if ":" in token:
                key, _, value = token.partition(":")
                if key and value:
                    parsed[key.strip()] = value.strip()
        return parsed

    def clean_query(self, query: str) -> str:
        if not self._strip_filters:
            return query
        return " ".join(token for token in query.split() if ":" not in token)
