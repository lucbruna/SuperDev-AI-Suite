"""Invoice export."""

from __future__ import annotations

import json
from typing import Any


class InvoiceExporter:
    def __init__(self) -> None:
        self._exports: list = []

    def export_json(self, invoice: dict[str, Any]) -> str:
        result = json.dumps(invoice, indent=2, default=str)
        self._exports.append({"format": "json", "invoice_id": invoice.get("id", "")})
        return result

    def export_csv(self, invoice: dict[str, Any]) -> str:
        lines = ["field,value"]
        for k, v in invoice.items():
            if isinstance(v, list):
                for item in v:
                    lines.append(f"{k},{item}")
            else:
                lines.append(f"{k},{v}")
        result = "\n".join(lines)
        self._exports.append({"format": "csv", "invoice_id": invoice.get("id", "")})
        return result

    def export_text(self, invoice: dict[str, Any]) -> str:
        lines = [
            f"Invoice: {invoice.get('number', '')}",
            f"Organization: {invoice.get('org_id', '')}",
            f"Total: {invoice.get('total', 0)}",
            "",
        ]
        for item in invoice.get("items", []):
            lines.append(f"  {item.get('description', '')}: {item.get('amount', 0)} x {item.get('quantity', 1)}")
        result = "\n".join(lines)
        self._exports.append({"format": "text", "invoice_id": invoice.get("id", "")})
        return result

    def get_export_history(self) -> list:
        return list(self._exports)
