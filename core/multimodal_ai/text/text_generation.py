from typing import Any, Optional
from datetime import datetime


class TextGenerator:
    def __init__(self) -> None:
        self._templates: dict[str, str] = {
            "greeting": "Hello! How can I assist you today?",
            "farewell": "Goodbye! Have a great day.",
            "confirmation": "The operation has been completed successfully.",
            "error": "An error occurred: {message}",
            "suggestion": "I suggest we {action} to improve {area}.",
        }

    def generate_response(self, intent: str, params: Optional[dict[str, Any]] = None) -> str:
        if params is None:
            params = {}
        responses: dict[str, str] = {
            "analyze_sales": f"Sales analysis complete. Revenue trends show {params.get('trend', 'stable')} performance.",
            "check_inventory": f"Current inventory level: {params.get('stock_level', 'unknown')} units.",
            "view_financial": f"Financial summary as of {datetime.now().strftime('%Y-%m-%d')}: {params.get('summary', 'All metrics within normal range.')}",
            "schedule_maintenance": f"Maintenance scheduled for {params.get('date', 'the next available slot')}.",
            "generate_report": f"Report generated: {params.get('report_name', 'Report')} is ready for review.",
            "send_message": f"Message sent to {params.get('recipient', 'recipient')}.",
            "manage_users": f"User operation completed for {params.get('user', 'the requested user')}.",
            "configure_system": f"System configuration updated: {params.get('setting', 'settings applied')}.",
            "order_supplies": f"Supply order placed. Order ID: {params.get('order_id', 'ORD-NEW')}.",
            "monitor_production": f"Production monitoring active. Current output: {params.get('output', 'normal')}.",
        }
        return responses.get(intent, self._templates["confirmation"])

    def generate_summary(self, data: dict[str, Any], max_points: int = 5) -> str:
        lines: list[str] = [f"Summary generated at {datetime.now().isoformat()}"]
        for key, value in list(data.items())[:max_points]:
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def generate_report(self, title: str, sections: dict[str, str]) -> str:
        report_parts: list[str] = [
            "=" * 60,
            f"  {title.upper()}",
            "=" * 60,
            "",
        ]
        for section_title, content in sections.items():
            report_parts.append(f"## {section_title}")
            report_parts.append(content)
            report_parts.append("")
        report_parts.append("=" * 60)
        report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(report_parts)

    def format_output(self, data: Any, format_type: str = "text") -> str:
        if format_type == "json":
            import json
            return json.dumps(data, indent=2, default=str)
        elif format_type == "table":
            if isinstance(data, list) and data:
                headers = list(data[0].keys()) if isinstance(data[0], dict) else ["value"]
                rows: list[list[str]] = []
                for item in data:
                    if isinstance(item, dict):
                        rows.append([str(item.get(h, "")) for h in headers])
                    else:
                        rows.append([str(item)])
                col_widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
                border = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
                header_row = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"
                result = [border, header_row, border]
                for row in rows:
                    result.append("| " + " | ".join(r.ljust(w) for r, w in zip(row, col_widths)) + " |")
                result.append(border)
                return "\n".join(result)
            return str(data)
        else:
            return str(data)

    def generate_suggestion(self, context: str, area: Optional[str] = None) -> str:
        suggestions: dict[str, list[str]] = {
            "sales": [
                "increase marketing spend on high-performing channels",
                "offer discounts on slow-moving inventory",
                "implement a customer loyalty program",
            ],
            "inventory": [
                "audit current stock levels and reorder points",
                "implement just-in-time inventory management",
                "review supplier contracts for better rates",
            ],
            "production": [
                "schedule preventive maintenance for all equipment",
                "optimize production line for bottleneck operations",
                "cross-train staff for flexible deployment",
            ],
            "finance": [
                "review recurring expenses for cost reduction",
                "optimize cash flow by adjusting payment terms",
                "explore refinancing options for existing debt",
            ],
            "general": [
                "schedule a team meeting to discuss priorities",
                "review current processes for efficiency improvements",
                "set up automated alerts for key metrics",
            ],
        }
        if area and area in suggestions:
            import random
            action = random.choice(suggestions[area])
            return self._templates["suggestion"].format(action=action, area=area)
        import re
        for topic, actions in suggestions.items():
            if topic in context.lower():
                import random
                action = random.choice(actions)
                return self._templates["suggestion"].format(action=action, area=topic)
        action = random.choice(suggestions["general"])
        return self._templates["suggestion"].format(action=action, area="operations")
