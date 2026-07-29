from typing import Any, Optional
import re


class VoiceRecognizer:
    def __init__(self) -> None:
        self._commands: dict[str, list[str]] = {
            "open_dashboard": ["open dashboard", "show dashboard", "go to dashboard"],
            "show_sales": ["show sales", "display sales", "sales report", "sales data"],
            "check_inventory": ["check inventory", "show stock", "inventory status"],
            "view_financial": ["show financial", "view finances", "financial report"],
            "schedule": ["schedule", "set appointment", "book meeting", "create event"],
            "send_message": ["send message", "send email", "compose message"],
            "search": ["search for", "find", "look up", "query"],
            "help": ["help", "what can you do", "commands"],
            "stop": ["stop", "cancel", "abort", "terminate"],
            "confirm": ["yes", "confirm", "proceed", "okay", "do it"],
            "reject": ["no", "reject", "cancel that", "never mind", "don't"],
        }
        self._profiles: dict[str, dict[str, Any]] = {}

    async def recognize_command(self, text: str) -> dict[str, Any]:
        text_lower = text.lower().strip()
        best_command = "unknown"
        best_score = 0
        for command, phrases in self._commands.items():
            score = max((1 if phrase in text_lower else 0) for phrase in phrases)
            if score > best_score:
                best_score = score
                best_command = command
        params = await self.extract_command_params(text)
        return {
            "command": best_command,
            "confidence": 0.9 if best_command != "unknown" else 0.1,
            "parameters": params,
            "raw_text": text,
        }

    async def extract_command_params(self, text: str) -> dict[str, Any]:
        params: dict[str, Any] = {}
        date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
        if date_match:
            params["date"] = date_match.group(1)
        time_match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)", text)
        if time_match:
            params["time"] = time_match.group(1)
        num_match = re.search(r"\b(\d+)\b", text)
        if num_match:
            params["number"] = int(num_match.group(1))
        product_match = re.search(r"(?:product|item|SKU)\s+([A-Za-z0-9-]+)", text, re.IGNORECASE)
        if product_match:
            params["product"] = product_match.group(1)
        return params

    async def match_command(self, text: str, command: str) -> bool:
        result = await self.recognize_command(text)
        return result["command"] == command

    def get_voice_profile(self, profile_id: str) -> Optional[dict[str, Any]]:
        return self._profiles.get(profile_id)
