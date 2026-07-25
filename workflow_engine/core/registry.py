from __future__ import annotations

from typing import Any, Optional, Type

from pydantic import BaseModel


class NodeTypeRegistration(BaseModel):
    type_name: str
    class_ref: type


class EdgeTypeRegistration(BaseModel):
    type_name: str
    class_ref: type


class WorkflowRegistry:
    def __init__(self):
        self._node_types: dict[str, type] = {}
        self._edge_types: dict[str, type] = {}

    def register_node_type(self, type_name: str, class_ref: type) -> None:
        self._node_types[type_name] = class_ref

    def register_edge_type(self, type_name: str, class_ref: type) -> None:
        self._edge_types[type_name] = class_ref

    def get_node_class(self, type_name: str) -> Optional[type]:
        return self._node_types.get(type_name)

    def get_edge_class(self, type_name: str) -> Optional[type]:
        return self._edge_types.get(type_name)

    def list_registered(self) -> dict[str, Any]:
        return {
            "node_types": list(self._node_types.keys()),
            "edge_types": list(self._edge_types.keys()),
        }