from enum import Enum
from typing import Any, Optional


class Intent(Enum):
    ANALYZE_SALES = "analyze_sales"
    CHECK_INVENTORY = "check_inventory"
    VIEW_FINANCIAL = "view_financial"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    GENERATE_REPORT = "generate_report"
    SEND_MESSAGE = "send_message"
    MANAGE_USERS = "manage_users"
    CONFIGURE_SYSTEM = "configure_system"
    ORDER_SUPPLIES = "order_supplies"
    MONITOR_PRODUCTION = "monitor_production"
    UNKNOWN = "unknown"


class IntentDetector:
    def __init__(self) -> None:
        self._intent_patterns: dict[Intent, list[str]] = {
            Intent.ANALYZE_SALES: [
                "sales", "revenue", "sell", "sold", "forecast", "pipeline",
            ],
            Intent.CHECK_INVENTORY: [
                "inventory", "stock", "warehouse", "supply", "quantity",
            ],
            Intent.VIEW_FINANCIAL: [
                "financial", "balance", "profit", "loss", "expense", "budget",
            ],
            Intent.SCHEDULE_MAINTENANCE: [
                "schedule", "maintenance", "repair", "service", "inspection",
            ],
            Intent.GENERATE_REPORT: [
                "report", "summary", "overview", "dashboard", "metrics",
            ],
            Intent.SEND_MESSAGE: [
                "send", "message", "email", "notify", "alert", "contact",
            ],
            Intent.MANAGE_USERS: [
                "user", "employee", "staff", "hire", "role", "permission",
            ],
            Intent.CONFIGURE_SYSTEM: [
                "configure", "setting", "setup", "install", "deploy",
            ],
            Intent.ORDER_SUPPLIES: [
                "order", "purchase", "buy", "procure", "supplies",
            ],
            Intent.MONITOR_PRODUCTION: [
                "production", "manufacturing", "output", "line", "machine",
            ],
        }

    def detect_intent(self, text: str) -> Intent:
        text_lower = text.lower()
        best_intent = Intent.UNKNOWN
        best_score = 0
        for intent, keywords in self._intent_patterns.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        return best_intent

    def classify_intent(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        results: dict[str, Any] = {}
        for intent, keywords in self._intent_patterns.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                results[intent.value] = score
        if not results:
            results[Intent.UNKNOWN.value] = 1
        return results

    def extract_parameters(self, text: str) -> dict[str, Any]:
        params: dict[str, Any] = {}
        date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        date_matches = __import__("re").findall(date_pattern, text)
        if date_matches:
            params["date"] = date_matches[0]
        money_pattern = r"[\$€£]\s?\d+(?:,\d{3})*(?:\.\d{2})?"
        money_matches = __import__("re").findall(money_pattern, text)
        if money_matches:
            params["amount"] = money_matches[0]
        number_matches = __import__("re").findall(r"\b\d+\b", text)
        if number_matches:
            params["numbers"] = [int(n) for n in number_matches]
        product_match = __import__("re").search(r"(?:product|item|sku)\s+(\w+)", text, __import__("re").IGNORECASE)
        if product_match:
            params["product_id"] = product_match.group(1)
        return params

    def get_confidence(self, text: str, intent: Optional[Intent] = None) -> float:
        if intent is None:
            intent = self.detect_intent(text)
        if intent == Intent.UNKNOWN:
            return 0.0
        text_lower = text.lower()
        keywords = self._intent_patterns.get(intent, [])
        matches = sum(1 for kw in keywords if kw in text_lower)
        return min(matches / max(len(keywords), 1), 1.0)
