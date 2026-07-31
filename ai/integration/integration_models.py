"""
Integration Models - Core data models
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class DataFormat(Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    PROTOBUF = "protobuf"
    BINARY = "binary"
    TEXT = "text"


@dataclass
class Endpoint:
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)
    body: Any = None
    timeout: int = 30
    retries: int = 3


@dataclass
class Response:
    status_code: int
    data: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""


@dataclass
class DataSource:
    source_id: str
    name: str
    source_type: str
    connection_string: str = ""
    format: DataFormat = DataFormat.JSON
    config: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


class IntegrationModels:
    def __init__(self):
        self.endpoints: dict[str, Endpoint] = {}
        self.data_sources: dict[str, DataSource] = {}
        self.schemas: dict[str, dict[str, Any]] = {}

    def create_endpoint(self, url: str, method: HttpMethod = HttpMethod.GET, **kwargs) -> Endpoint:
        endpoint_id = hashlib.sha256(f"{method.value}{url}".encode()).hexdigest()[:16]
        endpoint = Endpoint(url=url, method=method, **kwargs)
        self.endpoints[endpoint_id] = endpoint
        return endpoint

    def get_endpoint(self, endpoint_id: str) -> Endpoint | None:
        return self.endpoints.get(endpoint_id)

    def create_data_source(self, name: str, source_type: str, **kwargs) -> DataSource:
        source_id = hashlib.sha256(f"{name}{source_type}".encode()).hexdigest()[:16]
        source = DataSource(source_id=source_id, name=name, source_type=source_type, **kwargs)
        self.data_sources[source_id] = source
        return source

    def get_data_source(self, source_id: str) -> DataSource | None:
        return self.data_sources.get(source_id)

    def register_schema(self, name: str, schema: dict[str, Any]) -> None:
        self.schemas[name] = schema

    def get_schema(self, name: str) -> dict[str, Any] | None:
        return self.schemas.get(name)

    def list_endpoints(self) -> list[Endpoint]:
        return list(self.endpoints.values())

    def list_data_sources(self) -> list[DataSource]:
        return list(self.data_sources.values())

    def count(self) -> int:
        return len(self.endpoints) + len(self.data_sources)
