"""Processing engine (attached by the facade as ``processing``)."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.processing.base import Processor
from data_intelligence.processing.chain import ProcessingChain
from data_intelligence.processing.cleaning import (DefaultFiller,
                                                   DropEmptyProcessor,
                                                   TrimProcessor)
from data_intelligence.processing.enrichment import (CustomerSegmenter,
                                                     LocationEnricher)
from data_intelligence.processing.normalization import (EmailNormalizer,
                                                        NameNormalizer,
                                                        PhoneNormalizer,
                                                        UfNormalizer)
from data_intelligence.processing.validation import (EmailValidator,
                                                     RequiredFieldValidator)

BUILTINS: dict[str, type[Processor]] = {
    "trim": TrimProcessor,
    "defaults": DefaultFiller,
    "drop_empty": DropEmptyProcessor,
    "name": NameNormalizer,
    "email": EmailNormalizer,
    "uf": UfNormalizer,
    "phone": PhoneNormalizer,
    "segment": CustomerSegmenter,
    "location": LocationEnricher,
    "email_validator": EmailValidator,
    "required": RequiredFieldValidator,
}


class ProcessingEngine:
    """Processes records through named processor chains."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.registries: dict[str, ProcessingChain] = {}

    def register_chain(self, chain_id: str,
                       chain: ProcessingChain) -> None:
        self.registries[chain_id] = chain

    def build_chain(self, names: list[str],
                    **params: Any) -> ProcessingChain:
        """Builds a chain from builtin processor names."""
        chain = ProcessingChain()
        for name in names:
            klass = BUILTINS.get(name)
            if klass is None:
                raise ValueError(f"unknown processor: {name}")
            kwargs = params.get(name, {})
            chain.add(klass(**kwargs) if isinstance(kwargs, dict)
                      else klass())
        return chain

    def process(self, chain_id: str,
                records: list[dict[str, Any]]) -> dict[str, Any]:
        """Runs a registered chain over records and returns a summary."""
        chain = self.registries.get(chain_id)
        if chain is None:
            raise ValueError(f"unknown chain: {chain_id}")
        with self.metrics.timed(f"processing.{chain_id}"):
            output = chain.apply_many(records)
        result = {"chain_id": chain_id, "input": len(records),
                  "output": len(output), "rejected": len(chain.rejected),
                  "records": output}
        self.metrics.gauge(f"processing.output.{chain_id}", len(output))
        return result

    def process_many(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Runs every registered chain over the records."""
        summary: dict[str, Any] = {"records": records, "chains": {}}
        for chain_id in self.registries:
            result = self.process(chain_id, records)
            summary["chains"][chain_id] = {
                "input": result["input"], "output": result["output"],
                "rejected": result["rejected"]}
        return summary

    def stats(self) -> dict[str, Any]:
        return {"chains": list(self.registries)}
