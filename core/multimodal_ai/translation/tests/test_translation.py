import pytest
from datetime import datetime

from ..translation_engine import TranslationEngine
from ..language_detector import LanguageDetector
from ..translator import Translator
from ..localization import Localizer


@pytest.mark.asyncio
async def test_translation_engine_initialize_stop():
    engine = TranslationEngine()
    assert engine.state.running is False
    await engine.initialize()
    assert engine.state.running is True
    await engine.stop()
    assert engine.state.running is False


@pytest.mark.asyncio
async def test_translation_engine_detect_language():
    engine = TranslationEngine()
    await engine.initialize()
    result = await engine.detect_language("the cat is on the table")
    assert result["language"] == "en"
    assert 0 < result["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_translation_engine_translate():
    engine = TranslationEngine()
    await engine.initialize()
    result = await engine.translate("hello", source="en", target="pt")
    assert result["translated_text"] == "olá"
    assert result["cached"] is False


@pytest.mark.asyncio
async def test_translation_engine_translate_auto():
    engine = TranslationEngine()
    await engine.initialize()
    result = await engine.translate("hello", source="auto", target="pt")
    assert result["translated_text"] == "olá"
    assert result["source"] == "en"


@pytest.mark.asyncio
async def test_translation_engine_cache():
    engine = TranslationEngine()
    await engine.initialize()
    r1 = await engine.translate("hello", "en", "pt")
    r2 = await engine.translate("hello", "en", "pt")
    assert r2["cached"] is True


@pytest.mark.asyncio
async def test_translation_engine_not_running_raises():
    engine = TranslationEngine()
    with pytest.raises(RuntimeError, match="not running"):
        await engine.translate("hello", "en", "pt")


def test_language_detector_detect():
    ld = LanguageDetector()
    assert ld.detect_language("the cat sat on the mat") == "en"
    assert ld.detect_language("olá como você está") == "pt"
    assert ld.detect_language("hola cómo estás") == "es"


def test_language_detector_multiple():
    ld = LanguageDetector()
    results = ld.detect_multiple("the cat is playing", top_n=2)
    assert len(results) <= 2
    assert results[0]["language"] == "en"


def test_language_detector_supported():
    ld = LanguageDetector()
    langs = ld.get_supported_languages()
    assert len(langs) == 9
    assert "en" in langs
    assert "pt" in langs
    assert "ja" in langs


def test_translator_translate():
    t = Translator()
    assert t.translate("hello", "en", "pt") == "olá"
    assert t.translate("hello", "en", "en") == "hello"


def test_translator_translate_batch():
    t = Translator()
    results = t.translate_batch(["hello", "goodbye"], "en", "pt")
    assert results == ["olá", "tchau"]


def test_translator_translate_document():
    t = Translator()
    doc = "hello\ngoodbye"
    result = t.translate_document(doc, "en", "pt")
    assert "olá" in result
    assert "tchau" in result


def test_localizer_format_date():
    lz = Localizer()
    d = datetime(2026, 7, 29)
    assert lz.format_date(d, "en-US") == "07/29/2026"
    assert lz.format_date(d, "pt-BR") == "29/07/2026"
    assert lz.format_date(d, "ja-JP") == "2026/07/29"


def test_localizer_format_currency():
    lz = Localizer()
    usd = lz.format_currency(1234.56, "en-US")
    assert "$" in usd
    brl = lz.format_currency(1234.56, "pt-BR")
    assert "R$" in brl


def test_localizer_localize_content():
    lz = Localizer()
    content = "{{greeting}}, welcome!"
    result = lz.localize_content(content, "pt-BR")
    assert result == "Olá, welcome!"
    result_en = lz.localize_content(content, "en-US")
    assert result_en == "Hello, welcome!"