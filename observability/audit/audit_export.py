import json
import csv
import io
from typing import List
from .audit_manager import AuditEntry


class AuditExport:
    def to_json(self, entries: List[AuditEntry]) -> str:
        return json.dumps(
            [
                {
                    "id": e.id,
                    "action": e.action,
                    "actor_id": e.actor_id,
                    "resource_type": e.resource_type,
                    "resource_id": e.resource_id,
                    "details": e.details,
                    "timestamp": e.timestamp,
                }
                for e in entries
            ],
            indent=2,
            default=str,
        )

    def to_csv(self, entries: List[AuditEntry]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "action", "actor_id", "resource_type", "resource_id", "details", "timestamp"])
        for e in entries:
            writer.writerow([e.id, e.action, e.actor_id, e.resource_type, e.resource_id, json.dumps(e.details, default=str), e.timestamp])
        return output.getvalue()

    def to_markdown(self, entries: List[AuditEntry]) -> str:
        if not entries:
            return "No audit entries."
        lines = ["| id | action | actor_id | resource_type | resource_id | details | timestamp |",
                 "|---|---|---|---|---|---|---|"]
        for e in entries:
            details_str = json.dumps(e.details, default=str)[:80]
            lines.append(f"| {e.id[:8]}... | {e.action} | {e.actor_id} | {e.resource_type} | {e.resource_id} | {details_str} | {e.timestamp} |")
        return "\n".join(lines)
