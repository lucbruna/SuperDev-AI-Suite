from __future__ import annotations

import csv
import io
from typing import Any

from ..api_interfaces import IAPISerializer


class CSVSerializer(IAPISerializer):
    """CSV serializer/deserializer using stdlib csv module."""

    def serialize(self, data: Any, fmt: str = "csv") -> str:
        output = io.StringIO()
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, (list, tuple)) and data:
            if isinstance(data[0], dict):
                writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(output)
                for row in data:
                    if isinstance(row, (list, tuple)):
                        writer.writerow(row)
                    else:
                        writer.writerow([row])
        return output.getvalue()

    def deserialize(self, data: Any, fmt: str = "csv") -> list[dict[str, Any]]:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        reader = csv.DictReader(io.StringIO(data))
        return list(reader)

    def to_dict(self) -> dict[str, Any]:
        return {"serializer": "CSV"}
