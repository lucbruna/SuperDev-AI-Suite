from __future__ import annotations

from .language_engine import LanguageEngine


def create_default_language_engine() -> LanguageEngine:
    """Create a LanguageEngine preloaded with en_US, pt_BR and es_ES."""
    from .translations import en_US, es_ES, pt_BR

    engine = LanguageEngine()
    engine.register("en_US", en_US.EN_US_MESSAGES)
    engine.register("pt_BR", pt_BR.PT_BR_MESSAGES)
    engine.register("es_ES", es_ES.ES_ES_MESSAGES)
    engine.set_locale("en_US")
    return engine


__all__ = ["LanguageEngine", "create_default_language_engine"]
