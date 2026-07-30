from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from ..api_interfaces import IAPISerializer


class XMLSerializer(IAPISerializer):
    """Simple XML serializer/deserializer using stdlib ElementTree."""

    def serialize(self, data: Any, fmt: str = "xml") -> str:
        root = self._to_element("root", data)
        return ET.tostring(root, encoding="unicode", short_empty_elements=False)

    def _to_element(self, name: str, value: Any) -> ET.Element:
        elem = ET.Element(name)
        if isinstance(value, dict):
            for key, val in value.items():
                child = self._to_element(key, val)
                elem.append(child)
        elif isinstance(value, (list, tuple)):
            for item in value:
                child = self._to_element("item", item)
                elem.append(child)
        else:
            elem.text = str(value)
        return elem

    def deserialize(self, data: Any, fmt: str = "xml") -> dict[str, Any]:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        root = ET.fromstring(data)
        return self._from_element(root)

    def _from_element(self, elem: ET.Element) -> Any:
        children = list(elem)
        if not children:
            return elem.text or ""
        result: dict[str, Any] = {}
        for child in children:
            tag = child.tag
            val = self._from_element(child)
            if tag in result:
                existing = result[tag]
                if not isinstance(existing, list):
                    result[tag] = [existing]
                result[tag].append(val)
            else:
                result[tag] = val
        return result

    def to_dict(self) -> dict[str, Any]:
        return {"serializer": "XML"}
