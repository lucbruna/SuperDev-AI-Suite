from __future__ import annotations

from ..manager import ContextManager
from ..builder import ContextBuilder
from ..loader import ContextLoader
from ..optimizer import ContextOptimizer
from ..validator import ContextValidator
from ..window import ContextWindow
from ..compressor import ContextCompressor
from ..expander import ContextExpander
from ..ranker import ContextRanker
from ..filter import ContextFilter
from ..router import ContextRouter


class TestContextManager:
    def setup_method(self) -> None:
        self.manager = ContextManager()

    def test_build_and_get_context(self) -> None:
        ctx = self.manager.build_context("test", ["src1", "src2"])
        assert "sources" in ctx
        assert ctx["sources"] == ["src1", "src2"]
        assert self.manager.get_context("test") is ctx

    def test_list_contexts(self) -> None:
        self.manager.build_context("a", [])
        self.manager.build_context("b", [])
        assert set(self.manager.list_contexts()) == {"a", "b"}

    def test_remove_context(self) -> None:
        self.manager.build_context("x", [])
        assert self.manager.remove_context("x") is True
        assert self.manager.remove_context("nonexistent") is False

    def test_clear(self) -> None:
        self.manager.build_context("a", [])
        self.manager.build_context("b", [])
        self.manager.clear()
        assert self.manager.list_contexts() == []

    def test_snapshot(self) -> None:
        self.manager.build_context("a", [])
        snap = self.manager.snapshot()
        assert snap["context_count"] == 1

    def test_properties(self) -> None:
        assert isinstance(self.manager.builder, ContextBuilder)
        assert isinstance(self.manager.loader, ContextLoader)
        assert isinstance(self.manager.optimizer, ContextOptimizer)
        assert isinstance(self.manager.validator, ContextValidator)
        assert isinstance(self.manager.window, ContextWindow)
        assert isinstance(self.manager.compressor, ContextCompressor)
        assert isinstance(self.manager.expander, ContextExpander)
        assert isinstance(self.manager.ranker, ContextRanker)
        assert isinstance(self.manager.filter, ContextFilter)
        assert isinstance(self.manager.router, ContextRouter)


class TestContextBuilder:
    def setup_method(self) -> None:
        self.builder = ContextBuilder()

    def test_build(self) -> None:
        ctx = self.builder.build(["a", "b"])
        assert ctx["sources"] == ["a", "b"]
        assert "content" in ctx

    def test_build_from_dict(self) -> None:
        ctx = self.builder.build_from_dict({"k1": "v1", "k2": "v2"})
        assert ctx["content"]["k1"] == "v1"

    def test_merge(self) -> None:
        a = self.builder.build(["x"])
        b = self.builder.build(["y"])
        merged = self.builder.merge([a, b])
        assert merged["sources"] == ["x", "y"]

    def test_build_count(self) -> None:
        self.builder.build([])
        self.builder.build([])
        assert self.builder.build_count == 2

    def test_reset(self) -> None:
        self.builder.build([])
        self.builder.reset()
        assert self.builder.build_count == 0


class TestContextLoader:
    def setup_method(self) -> None:
        self.loader = ContextLoader()

    def test_load_text(self) -> None:
        result = self.loader.load_text("hello", "test")
        assert result["type"] == "text"
        assert result["content"] == "hello"
        assert result["source"] == "test"

    def test_load_dict(self) -> None:
        result = self.loader.load_dict({"a": 1}, "d")
        assert result["type"] == "dict"

    def test_load_list(self) -> None:
        result = self.loader.load_list([1, 2, 3], "l")
        assert result["type"] == "list"

    def test_load_batch(self) -> None:
        sources = [
            {"type": "text", "content": "hello", "name": "t1"},
            {"type": "dict", "data": {"k": "v"}, "name": "d1"},
        ]
        results = self.loader.load_batch(sources)
        assert len(results) == 2

    def test_reset(self) -> None:
        self.loader.load_text("hello")
        self.loader.reset()
        assert self.loader.load_count == 0


class TestContextOptimizer:
    def setup_method(self) -> None:
        self.optimizer = ContextOptimizer()

    def test_trim_duplicates(self) -> None:
        ctx = {"content": {"a": "same", "b": "same", "c": "diff"}, "metadata": {}}
        result = self.optimizer.trim_duplicates(ctx)
        keys = set(result["content"].keys())
        assert len(keys) <= 2

    def test_truncate_content(self) -> None:
        ctx = {"content": {"a": "x" * 5000, "b": "y" * 5000}, "metadata": {}}
        result = self.optimizer.truncate_content(ctx, max_chars=6000)
        total = sum(len(str(v)) for v in result["content"].values())
        assert total <= 6000

    def test_optimize(self) -> None:
        ctx = {"content": {"a": "hello", "b": "hello"}, "metadata": {}}
        result = self.optimizer.optimize(ctx)
        assert result["metadata"].get("optimized") is True

    def test_reset(self) -> None:
        self.optimizer.optimize({"content": {}, "metadata": {}})
        self.optimizer.reset()
        assert self.optimizer.optimization_count == 0


class TestContextValidator:
    def setup_method(self) -> None:
        self.validator = ContextValidator()

    def test_valid_context(self) -> None:
        result = self.validator.validate({"content": {}, "sources": []})
        assert result.valid is True

    def test_invalid_context(self) -> None:
        result = self.validator.validate({"content": {}})
        assert result.valid is False
        assert "sources" in result.errors[0]

    def test_validate_size(self) -> None:
        ctx = {"content": {"data": "x" * 1000}, "sources": ["a"]}
        result = self.validator.validate_size(ctx, max_size=100)
        assert result.valid is False

    def test_validate_schema(self) -> None:
        ctx = {"content": {}, "sources": []}
        schema = {"content": dict, "sources": list}
        result = self.validator.validate_schema(ctx, schema)
        assert result.valid is True

    def test_reset(self) -> None:
        self.validator.validate({"content": {}, "sources": []})
        self.validator.reset()
        assert self.validator.validation_count == 0


class TestContextWindow:
    def setup_method(self) -> None:
        self.window = ContextWindow(window_size=3)

    def test_slice(self) -> None:
        data = [1, 2, 3, 4, 5]
        assert self.window.slice(data, 0) == [1, 2, 3]
        assert self.window.slice(data, 2) == [3, 4, 5]

    def test_advance(self) -> None:
        self.window.advance(2)
        assert self.window.position == 2

    def test_reset(self) -> None:
        self.window.advance(5)
        self.window.reset()
        assert self.window.position == 0

    def test_window_count(self) -> None:
        assert self.window.window_count(10) == 4

    def test_sliding_windows(self) -> None:
        data = [1, 2, 3, 4, 5]
        windows = self.window.sliding_windows(data, stride=2)
        assert len(windows) == 2

    def test_context_chunks(self) -> None:
        ctx = {"content": {"a": 1, "b": 2, "c": 3, "d": 4}}
        chunks = self.window.context_chunks(ctx)
        assert len(chunks) == 2

    def test_window_size_setter(self) -> None:
        self.window.window_size = 5
        assert self.window.window_size == 5

    def test_window_size_setter_invalid(self) -> None:
        try:
            self.window.window_size = 0
            assert False, "Should raise ValueError"
        except ValueError:
            pass


class TestContextCompressor:
    def setup_method(self) -> None:
        self.compressor = ContextCompressor()

    def test_compress(self) -> None:
        ctx = {"content": {"a": "x" * 500}, "metadata": {}}
        result = self.compressor.compress(ctx)
        assert result["metadata"]["compressed"] is True
        assert len(result["content"]["a"]) < 200

    def test_summarize(self) -> None:
        text = "hello world " * 50
        s = self.compressor.summarize(text, max_length=50)
        assert len(s) < len(text)

    def test_compress_values(self) -> None:
        d = {"key": "x" * 500}
        result = self.compressor.compress_values(d, 50)
        assert len(result["key"]) < 100

    def test_reset(self) -> None:
        self.compressor.compress({"content": {}, "metadata": {}})
        self.compressor.reset()
        assert self.compressor.compression_count == 0


class TestContextExpander:
    def setup_method(self) -> None:
        self.expander = ContextExpander()

    def test_expand_entry(self) -> None:
        entry = {"content": {"a": 1}, "metadata": {}}
        result = self.expander.expand_entry(entry, {"b": 2})
        assert result["content"]["b"] == 2

    def test_expand_key(self) -> None:
        ctx = {"content": {"a": 1}, "metadata": {}}
        result = self.expander.expand_key(ctx, "b", 2)
        assert result["content"]["b"] == 2

    def test_expand_from_source(self) -> None:
        ctx = {"content": {"a": "hello"}, "metadata": {}}
        result = self.expander.expand_from_source(ctx, "a", "b")
        assert "b" in result["content"]

    def test_reset(self) -> None:
        self.expander.expand_key({"content": {}, "metadata": {}}, "a", 1)
        self.expander.reset()
        assert self.expander.expansion_count == 0


class TestContextRanker:
    def setup_method(self) -> None:
        self.ranker = ContextRanker()

    def test_rank_by_relevance(self) -> None:
        items = [
            {"content": "hello world", "source": "a"},
            {"content": "goodbye", "source": "b"},
        ]
        ranked = self.ranker.rank_by_relevance(items, "hello")
        assert ranked[0]["source"] == "a"

    def test_rank_by_recency(self) -> None:
        items = [
            {"metadata": {"timestamp": 100.0}},
            {"metadata": {"timestamp": 200.0}},
        ]
        ranked = self.ranker.rank_by_recency(items)
        assert ranked[0]["metadata"]["timestamp"] == 200.0

    def test_rank_by_importance(self) -> None:
        items = [
            {"metadata": {"importance": 0.5}},
            {"metadata": {"importance": 0.9}},
        ]
        ranked = self.ranker.rank_by_importance(items)
        assert ranked[0]["metadata"]["importance"] == 0.9

    def test_top_k(self) -> None:
        items = [{"i": 1}, {"i": 2}, {"i": 3}]
        assert len(self.ranker.top_k(items, 2)) == 2

    def test_reset(self) -> None:
        self.ranker.rank_by_relevance([{"content": "", "source": ""}], "x")
        self.ranker.reset()
        assert self.ranker.ranking_count == 0


class TestContextFilter:
    def setup_method(self) -> None:
        self.filter = ContextFilter()

    def test_filter_by_key(self) -> None:
        ctx = {"content": {"a": 1, "b": 2, "c": 3}, "metadata": {}}
        result = self.filter.filter_by_key(ctx, ["a", "c"])
        assert set(result["content"].keys()) == {"a", "c"}

    def test_filter_items(self) -> None:
        items = [{"type": "x"}, {"type": "y"}, {"type": "x"}]
        result = self.filter.filter_items(items, "type", "x")
        assert len(result) == 2

    def test_reset(self) -> None:
        self.filter.filter_by_key({"content": {}, "metadata": {}}, [])
        self.filter.reset()
        assert self.filter.filter_count == 0


class TestContextRouter:
    def setup_method(self) -> None:
        self.router = ContextRouter()

    def test_register_and_route(self) -> None:
        calls = []

        def handler(ctx: dict) -> str:
            calls.append(ctx)
            return "handled"

        self.router.register_route("test_type", handler)
        result = self.router.route({"type": "test_type"})
        assert result == "handled"
        assert len(calls) == 1

    def test_route_missing_key(self) -> None:
        try:
            self.router.route({"type": "unknown"})
            assert False, "Should raise KeyError"
        except KeyError:
            pass

    def test_unregister_route(self) -> None:
        self.router.register_route("x", lambda c: None)
        assert self.router.unregister_route("x") is True
        assert self.router.unregister_route("x") is False

    def test_list_routes(self) -> None:
        self.router.register_route("a", lambda c: None)
        self.router.register_route("b", lambda c: None)
        assert set(self.router.list_routes()) == {"a", "b"}

    def test_clear_routes(self) -> None:
        self.router.register_route("a", lambda c: None)
        self.router.clear_routes()
        assert self.router.list_routes() == []

    def test_reset(self) -> None:
        self.router.register_route("a", lambda c: None)
        self.router.route({"type": "a"})
        self.router.reset()
        assert self.router.route_count == 0
        assert self.router.list_routes() == []

    def test_route_by_source(self) -> None:
        def h(ctx: dict) -> str:
            return "ok"

        self.router.register_route("src1", h)
        result = self.router.route_by_source({"sources": ["src1", "src2"]})
        assert result == "ok"
