import pytest
from ..language_processor import LanguageProcessor
from ..intent_detection import IntentDetector, Intent
from ..semantic_analysis import SemanticAnalyzer
from ..text_generation import TextGenerator
from ..text_engine import TextEngine


class TestLanguageProcessor:
    def setup_method(self) -> None:
        self.processor = LanguageProcessor()

    def test_analyze_syntax(self) -> None:
        result = self.processor.analyze_syntax("Hello world. This is a test.")
        assert result["word_count"] == 6
        assert result["sentence_count"] == 2

    def test_extract_entities(self) -> None:
        text = "Contact support@example.com or call +1-555-1234. Order ORD-123456."
        entities = self.processor.extract_entities(text)
        labels = [e["label"] for e in entities]
        assert "EMAIL" in labels
        assert "ORDER_ID" in labels

    def test_detect_language(self) -> None:
        result = self.processor.detect_language("The quick brown fox jumps over the lazy dog")
        assert result["language"] == "es"

    def test_tokenize_and_lemmatize(self) -> None:
        tokens = self.processor.tokenize("running faster is better")
        assert "running" in tokens
        assert self.processor.lemmatize("running") == "run"
        assert self.processor.lemmatize("better") == "good"


class TestIntentDetector:
    def setup_method(self) -> None:
        self.detector = IntentDetector()

    def test_detect_intent_sales(self) -> None:
        intent = self.detector.detect_intent("What are our sales figures for this quarter?")
        assert intent == Intent.ANALYZE_SALES

    def test_detect_intent_inventory(self) -> None:
        intent = self.detector.detect_intent("Check the stock levels in warehouse B")
        assert intent == Intent.CHECK_INVENTORY

    def test_detect_intent_unknown(self) -> None:
        intent = self.detector.detect_intent("The weather is nice today")
        assert intent == Intent.UNKNOWN

    def test_extract_parameters_with_date(self) -> None:
        params = self.detector.extract_parameters("Show sales for 15/03/2026")
        assert "date" in params

    def test_get_confidence(self) -> None:
        conf = self.detector.get_confidence("Analyze our sales revenue pipeline")
        assert conf > 0


class TestSemanticAnalyzer:
    def setup_method(self) -> None:
        self.analyzer = SemanticAnalyzer()

    def test_get_sentiment_positive(self) -> None:
        result = self.analyzer.get_sentiment("This is excellent and fantastic progress")
        assert result["label"] == "positive"

    def test_get_sentiment_negative(self) -> None:
        result = self.analyzer.get_sentiment("This is a terrible failure and poor result")
        assert result["label"] == "negative"

    def test_summarize(self) -> None:
        text = "First sentence about sales. Second about inventory. Third about finance. Fourth about production."
        summary = self.analyzer.summarize(text, max_sentences=2)
        assert len(summary.split(". ")) <= 3

    def test_extract_meanings(self) -> None:
        result = self.analyzer.extract_meanings("sales revenue and profit growth")
        assert result["total_unique_words"] == 5


class TestTextGenerator:
    def setup_method(self) -> None:
        self.generator = TextGenerator()

    def test_generate_response_sales(self) -> None:
        response = self.generator.generate_response("analyze_sales", {"trend": "upward"})
        assert "upward" in response

    def test_generate_summary(self) -> None:
        summary = self.generator.generate_summary({"sales": 100, "cost": 50, "profit": 50})
        assert "sales" in summary

    def test_generate_report(self) -> None:
        report = self.generator.generate_report("Test Report", {"Intro": "Hello"})
        assert "TEST REPORT" in report


class TestTextEngine:
    @pytest.mark.asyncio
    async def test_process_text(self) -> None:
        engine = TextEngine()
        result = await engine.process_text("Show me the sales report for last quarter")
        assert result["intent"] == "analyze_sales"
        assert "sales" in str(result["semantics"])

    @pytest.mark.asyncio
    async def test_generate_response(self) -> None:
        engine = TextEngine()
        result = await engine.generate("Check inventory levels")
        assert result["intent"] == "check_inventory"

    @pytest.mark.asyncio
    async def test_engine_state(self) -> None:
        engine = TextEngine()
        assert engine.state.status == "idle"
        await engine.process_text("test")
        assert engine.metrics.texts_processed >= 1

    @pytest.mark.asyncio
    async def test_engine_config(self) -> None:
        engine = TextEngine()
        result = await engine.process_text("Bonjour le monde")
        assert result["language"]["language"] != ""
