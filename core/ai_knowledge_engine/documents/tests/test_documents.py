from __future__ import annotations

import pytest

from ..document_engine import DocumentEngine, EngineConfig, EngineState
from ..pdf_analyzer import PDFAnalyzer
from ..document_parser import DocumentParser
from ..summary_generator import SummaryGenerator
from ..information_extractor import InformationExtractor


@pytest.mark.asyncio
async def test_document_engine_initialize():
    engine = DocumentEngine()
    assert engine.state == EngineState.IDLE
    await engine.initialize()
    assert engine.state == EngineState.READY
    await engine.stop()
    assert engine.state == EngineState.IDLE


@pytest.mark.asyncio
async def test_document_engine_analyze_document():
    engine = DocumentEngine()
    await engine.initialize()
    result = await engine.analyze_document("This is a test document. It has some content. NLP is used.")
    assert "parsed" in result
    assert "extracted" in result
    assert "summary" in result
    assert engine.metrics.total_documents_processed == 1
    assert engine.metrics.successful_analyses == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_document_engine_extract_information():
    engine = DocumentEngine()
    await engine.initialize()
    result = await engine.extract_information("Contact us at test@example.com or visit https://example.com")
    assert "email" in result or "url" in result
    await engine.stop()


@pytest.mark.asyncio
async def test_document_engine_generate_summary():
    engine = DocumentEngine()
    await engine.initialize()
    text = "Machine learning is a subset of AI. It involves training models on data. Deep learning uses neural networks."
    result = await engine.generate_summary(text)
    assert result["type"] == "standard"
    assert result["summary_length"] > 0
    await engine.stop()


@pytest.mark.asyncio
async def test_document_engine_not_ready_raises():
    engine = DocumentEngine()
    with pytest.raises(RuntimeError, match="Engine not ready"):
        await engine.analyze_document("test")


@pytest.mark.asyncio
async def test_pdf_analyzer_analyze_pdf():
    pdf = PDFAnalyzer()
    result = await pdf.analyze_pdf("title=Research Paper\nsize=204800")
    assert "text" in result
    assert "metadata" in result
    assert result["metadata"]["title"] == "Research Paper"
    assert result["metadata"]["file_size_bytes"] == 204800


@pytest.mark.asyncio
async def test_pdf_analyzer_extract_images():
    pdf = PDFAnalyzer()
    images = await pdf.extract_images("This contains an image and a figure")
    assert len(images) >= 2


@pytest.mark.asyncio
async def test_document_parser_parse():
    parser = DocumentParser()
    result = await parser.parse("Hello world. This is a test.", "txt")
    assert result["format"] == "txt"
    assert result["word_count"] == 6
    assert result["language"] == "en"


@pytest.mark.asyncio
async def test_document_parser_unsupported_format():
    parser = DocumentParser()
    with pytest.raises(ValueError, match="Unsupported format"):
        await parser.parse("test", "xyz")


@pytest.mark.asyncio
async def test_document_parser_markdown_sections():
    parser = DocumentParser()
    md = "# Introduction\nSome intro text.\n## Details\nMore details here.\n# Conclusion\nFinal thoughts."
    result = await parser.parse(md, "md")
    assert len(result["sections"]) >= 2
    assert result["sections"][0]["title"] == "Introduction"


@pytest.mark.asyncio
async def test_summary_generator_generate_summary():
    sg = SummaryGenerator()
    text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
    result = await sg.generate_summary(text)
    assert result["type"] == "standard"
    assert result["original_length"] > result["summary_length"]


@pytest.mark.asyncio
async def test_summary_generator_executive_summary():
    sg = SummaryGenerator()
    text = "The first key finding is important. The second finding confirms our hypothesis. The third data point supports this."
    result = await sg.generate_executive_summary(text)
    assert result["type"] == "executive"
    assert len(result["executive_summary"]) > 0


@pytest.mark.asyncio
async def test_summary_generator_extract_key_points():
    sg = SummaryGenerator()
    text = "Point one is crucial. Point two is also important. Point three cannot be ignored. Point four is relevant."
    result = await sg.extract_key_points(text, max_points=3)
    assert result["count"] <= 3
    assert len(result["key_points"]) > 0


@pytest.mark.asyncio
async def test_information_extractor_extract_entities():
    ie = InformationExtractor()
    text = "Email us at info@example.com or call +1-555-123-4567. Visit https://test.com."
    result = await ie.extract_entities(text)
    assert "email" in result
    assert "url" in result


@pytest.mark.asyncio
async def test_information_extractor_dates_and_values():
    ie = InformationExtractor()
    text = "On 2024-01-15 the price was $100. 95% of tests passed."
    dates = await ie.extract_dates(text)
    assert "2024-01-15" in dates
    values = await ie.extract_values(text, "percentage")
    assert "95%" in values


@pytest.mark.asyncio
async def test_information_extractor_relationships():
    ie = InformationExtractor()
    text = "Python is a programming language. Training leads to accuracy."
    rels = await ie.extract_relationships(text)
    assert isinstance(rels, list)


@pytest.mark.asyncio
async def test_information_extractor_tables():
    ie = InformationExtractor()
    text = "| Name | Age | City |\n| John | 30  | NYC  |"
    tables = await ie.extract_tables(text)
    assert len(tables) > 0


@pytest.mark.asyncio
async def test_information_extractor_unknown_value_type():
    ie = InformationExtractor()
    with pytest.raises(ValueError, match="Unknown value type"):
        await ie.extract_values("test", "invalid_type")


@pytest.mark.asyncio
async def test_document_engine_metrics():
    engine = DocumentEngine(config=EngineConfig(max_file_size_mb=10))
    await engine.initialize()
    await engine.analyze_document("Test document for metrics. It has some text content.")
    assert engine.metrics.total_documents_processed == 1
    assert engine.metrics.successful_analyses == 1
    assert engine.metrics.average_processing_time_ms >= 0
    assert engine.config.max_file_size_mb == 10
    await engine.stop()