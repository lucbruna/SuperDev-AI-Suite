"""Document parsing (pure-python text extraction)."""

from __future__ import annotations

from typing import Any


class DocumentParser:
    """Extracts plain text and metadata from common file types."""

    PLAIN_TYPES = {"txt", "md", "csv", "json", "log", "py", "sql"}

    def __init__(self, max_size: int = 1_000_000) -> None:
        self.max_size = max_size

    def parse(self, filename: str, content: str) -> dict[str, Any]:
        file_type = (filename.rsplit(".", 1)[-1]
                     if "." in filename else "txt").lower()
        text = self._extract(content, file_type)
        return {"title": filename, "content": text,
                "file_type": file_type,
                "size": len(text)}

    def _extract(self, content: str, file_type: str) -> str:
        content = (content or "")[: self.max_size]
        if file_type == "html":
            return self._strip_html(content)
        if file_type == "json":
            return self._flatten_json(content)
        return content

    @staticmethod
    def _strip_html(content: str) -> str:
        import re
        text = re.sub(r"<script.*?</script>", " ", content, flags=re.S)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _flatten_json(content: str) -> str:
        import json
        try:
            data = json.loads(content)
        except ValueError:
            return content

        def walk(value: Any, prefix: str = "") -> list[str]:
            if isinstance(value, dict):
                parts = []
                for key, item in value.items():
                    parts.extend(walk(item, f"{prefix}{key}."))
                return parts
            if isinstance(value, list):
                return [walk(item, f"{prefix}") for item in value]  # type: ignore[return-value]
            return [f"{prefix}{value}"] if value is not None else []

        return " ".join(str(part) for part in walk(data))
