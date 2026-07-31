"""Transformation engine: facade over mappers, normalizers, and renderers."""

from __future__ import annotations

import logging
from typing import Any

from .mapper import FieldMapper
from .normalizer import Normalizer
from .schema_mapper import SchemaMapper
from .template import TemplateRenderer


class TransformationEngine:
    """Facade for the transformation subsystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.transformation")
        self.normalizer = Normalizer()
        self.templates = TemplateRenderer()

    def field_map(self) -> FieldMapper:
        return FieldMapper()

    def schema_map(self) -> SchemaMapper:
        return SchemaMapper()

    def transform(self, mapper: FieldMapper | SchemaMapper,
                  record: dict[str, Any]) -> dict[str, Any]:
        return mapper.apply(record) if isinstance(mapper, FieldMapper) \
            else mapper.convert(record)

    def render(self, template: str, data: dict[str, Any]) -> str:
        return self.templates.render(template, data)
