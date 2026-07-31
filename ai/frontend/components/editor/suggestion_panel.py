"""
AI Suggestion Panel
"""
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class SuggestionType(Enum):
    COMPLETION = "completion"
    FIX = "fix"
    REFACTOR = "refactor"
    EXPLAIN = "explain"
    DOCUMENT = "document"
    TEST = "test"
    OPTIMIZE = "optimize"
    SECURITY = "security"


class SuggestionPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Suggestion:
    id: str
    type: SuggestionType
    title: str
    description: str = ""
    code: str = ""
    original_code: str = ""
    file_path: str = ""
    line: int = 0
    priority: SuggestionPriority = SuggestionPriority.MEDIUM
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_acceptable(self):
        return self.confidence >= 0.7


class SuggestionPanel:
    def __init__(self):
        self.suggestions = []
        self.selected_suggestion = None
        self.auto_apply = False
        self.listeners = []
        
    def add_suggestion(self, suggestion):
        self.suggestions.append(suggestion)
        self._emit("suggestion_added", {"suggestion": suggestion})
        
    def remove_suggestion(self, suggestion_id):
        for i, s in enumerate(self.suggestions):
            if s.id == suggestion_id:
                removed = self.suggestions.pop(i)
                self._emit("suggestion_removed", {"suggestion": removed})
                return True
        return False
        
    def accept_suggestion(self, suggestion_id):
        suggestion = next((s for s in self.suggestions if s.id == suggestion_id), None)
        if suggestion:
            self._emit("suggestion_accepted", {"suggestion": suggestion})
            self.remove_suggestion(suggestion_id)
            return True
        return False
        
    def reject_suggestion(self, suggestion_id):
        suggestion = next((s for s in self.suggestions if s.id == suggestion_id), None)
        if suggestion:
            self._emit("suggestion_rejected", {"suggestion": suggestion})
            self.remove_suggestion(suggestion_id)
            return True
        return False
        
    def dismiss_all(self):
        self.suggestions.clear()
        self._emit("suggestions_cleared", {})
        
    def filter_suggestions(self, type_filter=None, priority_filter=None, min_confidence=0.5):
        results = self.suggestions
        if type_filter:
            results = [s for s in results if s.type == type_filter]
        if priority_filter:
            results = [s for s in results if s.priority == priority_filter]
        results = [s for s in results if s.confidence >= min_confidence]
        return results
        
    def sort_by_confidence(self):
        return sorted(self.suggestions, key=lambda s: s.confidence, reverse=True)
        
    def select(self, suggestion_id):
        self.selected_suggestion = next((s for s in self.suggestions if s.id == suggestion_id), None)
        if self.selected_suggestion:
            self._emit("suggestion_selected", {"suggestion": self.selected_suggestion})
        return self.selected_suggestion
        
    def on(self, event, callback):
        self.listeners.append({"event": event, "callback": callback})
        
    def _emit(self, event, data):
        for listener in self.listeners:
            if listener["event"] == event:
                listener["callback"](data)
