"""Tax rules for the Finance Intelligence Engine (Volume 35).

Brazilian fiscal regime tables for ICMS, ISS, PIS, COFINS, IRPJ, CSLL.
"""

from __future__ import annotations

from finance_intelligence.finance_models import FiscalRegime


class TaxRules:
    """Rate tables and applicability rules per fiscal regime."""

    _RATES: dict[FiscalRegime, dict[str, float]] = {
        FiscalRegime.SIMPLES_NACIONAL: {
            "PIS": 0.0, "COFINS": 0.0, "IRPJ": 0.0, "CSLL": 0.0,
            "ICMS": 0.04, "ISS": 0.05, "SIMPLES": 0.06,
        },
        FiscalRegime.LUCRO_PRESUMIDO: {
            "PIS": 0.0065, "COFINS": 0.03, "IRPJ": 0.012,
            "CSLL": 0.0108, "ICMS": 0.18, "ISS": 0.05, "SIMPLES": 0.0,
        },
        FiscalRegime.LUCRO_REAL: {
            "PIS": 0.0165, "COFINS": 0.076, "IRPJ": 0.25,
            "CSLL": 0.09, "ICMS": 0.18, "ISS": 0.05, "SIMPLES": 0.0,
        },
    }

    def __init__(self, regime: FiscalRegime = FiscalRegime.SIMPLES_NACIONAL
                 ) -> None:
        self.regime = regime

    def rate(self, tax: str) -> float:
        return self._RATES[self.regime].get(tax, 0.0)

    def applies(self, tax: str) -> bool:
        return self.rate(tax) > 0.0

    def applicable_taxes(self) -> list[str]:
        return [tax for tax in self._RATES[self.regime]
                if self.applies(tax)]

    def set_regime(self, regime: FiscalRegime) -> None:
        self.regime = regime
