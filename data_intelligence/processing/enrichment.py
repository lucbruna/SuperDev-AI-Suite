"""Enrichment processors (customer segmentation, location)."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_protocols import coerce_number
from data_intelligence.processing.base import Processor


class CustomerSegmenter(Processor):
    """Classifies a customer by purchase behaviour.

    Rules (default):
        * ``Cliente recorrente`` - 2+ purchases or known flag.
        * ``Cliente alto valor``  - total value above the threshold.
        * ``Cliente novo``        - otherwise.

    Output goes to ``segment``.
    """

    name = "segment"

    def __init__(self, purchases_field: str = "purchases",
                 value_field: str = "total_value",
                 output: str = "segment",
                 high_value_threshold: float = 5000.0) -> None:
        self.purchases_field = purchases_field
        self.value_field = value_field
        self.output = output
        self.threshold = high_value_threshold

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        purchases = coerce_number(out.get(self.purchases_field, 0)) or 0
        value = coerce_number(out.get(self.value_field, 0)) or 0
        if value >= self.threshold:
            out[self.output] = "Cliente alto valor"
        elif purchases >= 2:
            out[self.output] = "Cliente recorrente"
        else:
            out[self.output] = "Cliente novo"
        return out


class LocationEnricher(Processor):
    """Adds ``region`` from a UF/state value (north, northeast, ...)."""

    name = "location"

    _REGIONS = {
        "south": {"RS", "SC", "PR"},
        "southeast": {"SP", "RJ", "MG", "ES"},
        "midwest": {"DF", "GO", "MT", "MS"},
        "northeast": {"BA", "PE", "CE", "MA", "RN", "PB", "PI", "AL", "SE"},
        "north": {"AM", "PA", "AC", "RO", "RR", "AP", "TO"},
    }

    def __init__(self, uf_field: str = "uf", output: str = "region") -> None:
        self.uf_field = uf_field
        self.output = output

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        value = out.get(self.uf_field)
        if isinstance(value, str):
            uf = value.strip().upper()
            for region, ufs in self._REGIONS.items():
                if uf in ufs:
                    out[self.output] = region
                    break
        return out
