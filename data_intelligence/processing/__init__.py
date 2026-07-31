"""Processing subsystem (Volume 22).

Normalizes, cleans, enriches and validates records (names, emails, UFs,
customer segments, ...).
"""

from __future__ import annotations

from data_intelligence.processing.base import (ProcessingError, Processor)
from data_intelligence.processing.chain import ProcessingChain
from data_intelligence.processing.cleaning import (DefaultFiller,
                                                   DropEmptyProcessor,
                                                   TrimProcessor)
from data_intelligence.processing.engine import (BUILTINS, ProcessingEngine)
from data_intelligence.processing.enrichment import (CustomerSegmenter,
                                                     LocationEnricher)
from data_intelligence.processing.normalization import (EmailNormalizer,
                                                        NameNormalizer,
                                                        PhoneNormalizer,
                                                        UfNormalizer)
from data_intelligence.processing.validation import (EmailValidator,
                                                     RequiredFieldValidator)

__all__ = [
    "ProcessingEngine", "ProcessingChain", "Processor", "ProcessingError",
    "BUILTINS", "TrimProcessor", "DefaultFiller", "DropEmptyProcessor",
    "NameNormalizer", "EmailNormalizer", "UfNormalizer", "PhoneNormalizer",
    "CustomerSegmenter", "LocationEnricher", "EmailValidator",
    "RequiredFieldValidator",
]
