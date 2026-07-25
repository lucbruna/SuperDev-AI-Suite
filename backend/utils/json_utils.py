import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        return super().default(obj)


def json_dumps(data: Any, **kwargs: Any) -> str:
    return json.dumps(data, cls=CustomJSONEncoder, **kwargs)


def json_loads(data: str | bytes, **kwargs: Any) -> Any:
    return json.loads(data, **kwargs)
