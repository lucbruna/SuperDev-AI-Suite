"""Manager for documentation lifecycle."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import DocPage, DocumentationConfig


class DocumentationManager:
    """Manages documentation pages and configurations."""

    def __init__(self):
        self._pages: Dict[str, DocPage] = {}
        self._configs: Dict[str, DocumentationConfig] = {}
        self._history: List[Dict[str, Any]] = []

    def add_page(self, page: DocPage) -> None:
        self._pages[page.page_id] = page
        self._record_action("add_page", page.page_id)

    def get_page(self, page_id: str) -> Optional[DocPage]:
        return self._pages.get(page_id)

    def remove_page(self, page_id: str) -> bool:
        if page_id in self._pages:
            del self._pages[page_id]
            self._record_action("remove_page", page_id)
            return True
        return False

    def add_config(self, config: DocumentationConfig) -> None:
        self._configs[config.config_id] = config

    def get_config(self, config_id: str) -> Optional[DocumentationConfig]:
        return self._configs.get(config_id)

    def list_pages(self) -> List[DocPage]:
        return list(self._pages.values())

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "pages": len(self._pages),
            "configs": len(self._configs),
        }

    def _record_action(self, action: str, target: str) -> None:
        self._history.append({
            "action": action,
            "target": target,
            "timestamp": datetime.utcnow().isoformat(),
        })
