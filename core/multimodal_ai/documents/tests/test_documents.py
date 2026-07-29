import pytest
from ..document_ai import DocumentAI, EngineState
from ..pdf_reader import PDFReader
from ..table_extractor import TableExtractor
from ..contract_analyzer import ContractAnalyzer
from ..document_classifier import DocumentClassifier


@pytest.fixture
def sample_document():
    return {
        "id": "doc-001",
        "type": "INVOICE",
        "name": "invoice_q1_2026.pdf",
        "path": "/docs/invoice_q1_2026.pdf",
        "pages": 5,
        "content": "Sample invoice content",
        "confidence": 0.95,
    }


@pytest.mark.asyncio
async def test_document_ai_initialize():
    ai = DocumentAI()
    assert ai.state == EngineState.STOPPED
    await ai.initialize()
    assert ai.state == EngineState.RUNNING
    await ai.stop()
    assert ai.state == EngineState.STOPPED


@pytest.mark.asyncio
async def test_document_ai_process_document(sample_document):
    ai = DocumentAI()
    await ai.initialize()
    result = await ai.process_document(sample_document)
    assert result["document_id"] == "doc-001"
    assert result["status"] == "processed"
    assert ai.metrics.documents_processed == 1
    await ai.stop()


@pytest.mark.asyncio
async def test_document_ai_analyze(sample_document):
    ai = DocumentAI()
    await ai.initialize()
    result = await ai.analyze(sample_document, "full")
    assert "sections" in result
    assert len(result["sections"]) == 3
    await ai.stop()


@pytest.mark.asyncio
async def test_document_ai_extract_data(sample_document):
    ai = DocumentAI()
    await ai.initialize()
    result = await ai.extract_data(sample_document, ["type", "pages"])
    assert result["fields"]["type"] == "INVOICE"
    assert result["fields"]["pages"] == 5
    await ai.stop()


@pytest.mark.asyncio
async def test_document_ai_classify(sample_document):
    ai = DocumentAI()
    await ai.initialize()
    result = await ai.classify(sample_document)
    assert result["document_type"] == "INVOICE"
    assert result["confidence"] == 0.95
    await ai.stop()


@pytest.mark.asyncio
async def test_pdf_reader_read_and_extract():
    reader = PDFReader()
    doc = await reader.read_pdf("/test/doc.pdf")
    assert doc["status"] == "read"
    assert doc["pages"] == 5
    text = await reader.extract_text(doc, page=1)
    assert "Sample text content" in text
    images = await reader.extract_images(doc)
    assert len(images) == 10
    metadata = await reader.get_pdf_metadata(doc)
    assert metadata["page_count"] == 5
    annotations = await reader.extract_annotations(doc)
    assert len(annotations) == 5


@pytest.mark.asyncio
async def test_table_extractor():
    extractor = TableExtractor()
    doc = {"id": "doc-t1"}
    tables = await extractor.extract_tables(doc)
    assert len(tables) == 3
    parsed = await extractor.parse_table(tables[0])
    assert len(parsed) == 4
    assert "Product" in parsed[0]
    cell = await extractor.extract_cells(tables[0], 0, 1)
    assert cell == "1200"
    cell_missing = await extractor.extract_cells(tables[0], 99, 0)
    assert cell_missing is None
    structure = await extractor.detect_table_structure(tables[0])
    assert structure["row_count"] == 4
    assert structure["column_count"] == 4


@pytest.mark.asyncio
async def test_contract_analyzer():
    analyzer = ContractAnalyzer()
    doc = {"id": "contract-001", "pages": 10}
    result = await analyzer.analyze_contract(doc)
    assert result["document_id"] == "contract-001"
    assert result["clause_count"] == 10
    assert len(result["risks"]) == 10
    assert result["risk_score"] > 0
    compliance = await analyzer.check_compliance(doc)
    assert compliance["compliant"] is True
    assert "gdpr" in compliance["standards_checked"]


@pytest.mark.asyncio
async def test_contract_analyzer_summary():
    analyzer = ContractAnalyzer()
    doc = {"id": "contract-002"}
    summary = await analyzer.get_contract_summary(doc)
    assert "contract-002" in summary


@pytest.mark.asyncio
async def test_document_classifier(sample_document):
    classifier = DocumentClassifier()
    result = await classifier.classify_document(sample_document)
    assert result["document_type"] == "INVOICE"
    assert result["confidence"] == 0.95


@pytest.mark.asyncio
async def test_document_classifier_auto_detect():
    classifier = DocumentClassifier()
    doc = {"name": "employment_agreement.pdf"}
    doc_type = await classifier.get_document_type(doc)
    assert doc_type == "CONTRACT"


@pytest.mark.asyncio
async def test_document_classifier_fallback():
    classifier = DocumentClassifier()
    doc = {"name": "unknown_file.txt"}
    doc_type = await classifier.get_document_type(doc)
    assert doc_type == "REPORT"