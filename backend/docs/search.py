from __future__ import annotations

from typing import Any


class DocSearch:
    def __init__(self):
        self._index: dict[str, list[dict[str, Any]]] = {}
        self._documents: dict[str, str] = {}

    def index_document(self, doc_id: str, content: str) -> None:
        self._documents[doc_id] = content
        words = set(content.lower().split())
        for word in words:
            if len(word) < 3:
                continue
            if word not in self._index:
                self._index[word] = []
            self._index[word].append({"doc_id": doc_id, "position": content.lower().find(word)})

    def index_module(self, mod_path: str, mod_data: dict[str, Any]) -> None:
        text = mod_path + "\n"
        if "classes" in mod_data:
            for cls in mod_data["classes"]:
                text += f"{cls['name']} {' '.join(cls['methods'])} {cls['doc']}\n"
        if "functions" in mod_data:
            for fn in mod_data["functions"]:
                text += f"{fn['name']} {' '.join(fn['args'])} {fn['doc']}\n"
        self.index_document(mod_path, text)

    def index_markdown(self, md_text: str, doc_id: str = "readme") -> None:
        import re
        text = re.sub(r"[#*`\[\]()]", " ", md_text)
        self.index_document(doc_id, text)

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        query_words = [w.lower() for w in query.split() if len(w) >= 3]
        if not query_words:
            return []
        scores: dict[str, int] = {}
        for word in query_words:
            results = self._index.get(word, [])
            for r in results:
                doc_id = r["doc_id"]
                scores[doc_id] = scores.get(doc_id, 0) + 1
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [{"doc_id": doc_id, "score": score, "preview": self._preview(doc_id, query)} for doc_id, score in ranked[:limit]]

    def _preview(self, doc_id: str, query: str) -> str:
        content = self._documents.get(doc_id, "")
        idx = content.lower().find(query.lower())
        if idx == -1:
            return content[:150]
        start = max(0, idx - 60)
        end = min(len(content), idx + len(query) + 90)
        preview = content[start:end]
        if start > 0:
            preview = "..." + preview
        if end < len(content):
            preview = preview + "..."
        return preview

    def autocomplete(self, prefix: str, limit: 5) -> list[str]:
        prefix = prefix.lower()
        matches = [word for word in self._index if word.startswith(prefix)]
        return sorted(matches)[:limit]

    @property
    def document_count(self) -> int:
        return len(self._documents)

    def clear(self) -> None:
        self._index.clear()
        self._documents.clear()
