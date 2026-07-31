from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .code_config import CodeConfig
from .code_manager import CodeManager
from .code_models import CodeFile, CodeIssue
from .code_registry import CodeRegistry
from .code_scanner import CodeScanner
from .parsing.ast_manager import ASTManager
from .understanding import CodeUnderstanding, ContextBuilder, DependencyGraph, PromptBuilder, SymbolIndex
from .understanding.symbol_index import RELEVANCE_WEIGHTS

if TYPE_CHECKING:
    from ai.llm import LLMEngine


def _module_to_path_map(files: list[CodeFile], root: str) -> dict[str, str]:
    """Map import module names to the file paths that define them.

    ``services/order_service.py`` becomes ``services.order_service``; a
    package's ``__init__.py`` becomes the package name itself. Files outside
    *root* are skipped.
    """
    root_path = Path(root).resolve()
    mapping: dict[str, str] = {}
    for file in files:
        try:
            rel = Path(file.path).resolve().relative_to(root_path)
        except ValueError:
            continue
        parts = list(rel.parts)
        name = (".".join(parts[:-1]) if parts[-1] == "__init__.py"
                else ".".join(parts[:-1] + [Path(parts[-1]).stem]))
        mapping.setdefault(name, file.path)
    return mapping


def _resolve_import_to_path(
    rel: Path,
    imp: dict[str, Any],
    module_map: dict[str, str],
) -> str | None:
    """Resolve a parsed import to a scanned file path (or ``None``).

    Handles absolute imports (``import a.b`` / ``from a.b import c``), the
    ``from pkg import submodule`` form, and **relative imports**
    (``from . import X`` / ``from ..pkg import Y``) using the ``level``
    recorded by :class:`ASTManager`. Sub-module packages resolve through
    their ``__init__.py`` (mapped by :func:`_module_to_path_map`).
    """
    module = imp.get("module") or ""
    names = imp.get("names") or []
    level = int(imp.get("level") or 0)

    if level == 0:
        # ``from services import order_service`` targets the submodule first;
        # ``from a.b import func`` falls back to the ``a.b`` module file.
        candidates = ([f"{module}.{names[0]}"] if module and names else []) + [module]
        for cand in candidates:
            path = module_map.get(cand)
            if path is not None:
                return path
        return None

    # Relative import: base package = the file's dirs minus (level - 1).
    dir_parts = list(rel.parts[:-1])
    if not dir_parts and level > 1:
        return None
    base = dir_parts[: max(0, len(dir_parts) - (level - 1))]
    base_pkg = ".".join(base)

    target = module or (names[0] if names else "")
    if not target:
        return None
    candidate = f"{base_pkg}.{target}" if base_pkg else target
    path = module_map.get(candidate)
    if path is not None:
        return path
    # ``from . import X`` where X is defined in the package ``__init__.py``.
    if module == (names[0] if names else None) and base_pkg:
        return module_map.get(base_pkg)
    return None


def _rank_selection(
    selection: list[dict[str, Any]],
    index: SymbolIndex,
    query: str | None,
) -> list[dict[str, Any]]:
    """Re-rank *selection* by symbol relevance to *query*.

    Each selected file is scored by the symbols matching *query* that are
    defined there, using :meth:`SymbolIndex.rank` (weighted by kind:
    ``class`` > ``function`` > ``import``). Seed files (depth 0) keep their
    position; the remaining files are sorted by descending relevance,
    preserving BFS order for ties. Every entry gains ``relevance`` (score)
    and ``matched_symbols`` (names).
    """
    query = (query or "").strip()
    if not query:
        return [{**entry, "relevance": 0, "matched_symbols": []}
                for entry in selection]

    # path -> (score, set of matched symbol names)
    scores: dict[str, tuple[int, set[str]]] = {}
    for match in index.rank(query):
        name = match["name"]
        for loc in match["locations"]:
            path = loc.get("path", "")
            weight = RELEVANCE_WEIGHTS.get(loc.get("kind", ""), 1)
            score, names = scores.get(path, (0, set()))
            if name not in names:
                scores[path] = (score + weight, names | {name})

    def score(entry: dict[str, Any]) -> tuple[int, list[str]]:
        value, names = scores.get(entry.get("path", ""), (0, set()))
        return value, sorted(names)

    seeds = [entry for entry in selection if entry.get("depth") == 0]
    others = [entry for entry in selection if entry.get("depth") != 0]
    others = sorted(others, key=lambda e: (-score(e)[0], e.get("depth", 0)))

    ranked: list[dict[str, Any]] = []
    for entry in seeds + others:
        value, names = score(entry)
        ranked.append({**entry, "relevance": value, "matched_symbols": names})
    return ranked


class CodeEngine:
    """Central orchestrator for code analysis, generation and LLM context."""

    def __init__(self, config: CodeConfig | None = None) -> None:
        self.config = config or CodeConfig()
        self.manager = CodeManager()
        self.registry = CodeRegistry()
        self.scanner = CodeScanner(config=self.config)
        self.understanding = CodeUnderstanding()
        # Lazy import: code_factory imports CodeEngine at module level.
        from .code_factory import CodeFactory

        self.factory = CodeFactory()
        self._llm: LLMEngine | None = None
        self._log = logging.getLogger("superdev.code.engine")

    # -- core API ---------------------------------------------------------

    async def scan_project(self, path: str) -> list[CodeFile]:
        return self.manager.scan(path)

    async def analyze(self, files: list[CodeFile]) -> list[CodeIssue]:
        return self.manager.analyze(files)

    async def generate(self, spec: dict[str, Any]) -> list[CodeFile]:
        return self.manager.generate(spec)

    # -- LLM code navigation (SymbolIndex + DependencyGraph + BFS + prompt) ----

    async def understand(self, path: str) -> dict[str, Any]:
        """Scan *path* and build the symbol index + dependency graph.

        Returns ``files`` (count), ``symbols``, ``symbol_count``, ``graph``
        and ``graph_summary`` (see :meth:`CodeUnderstanding.understand`).
        """
        return self.understanding.understand(path)

    async def find_symbols(self, path: str, query: str) -> dict[str, Any]:
        """Index *path* and search symbols whose names contain *query*.

        Matches come back **already sorted by relevance** (descending)
        via :meth:`SymbolIndex.rank` — a class defined in two files
        outranks a function, which outranks a mere import. Each match is
        ``{name, locations, relevance}``. Also returns ``symbols`` (total
        indexed) and ``files``.
        """
        files = await self.scan_project(path)
        index = SymbolIndex()
        index.index_files(files)
        return {
            "query": query,
            "matches": index.rank(query),
            "symbols": index.count(),
            "files": len(files),
        }

    async def build_llm_context(
        self,
        path: str,
        seed_files: list[str] | None = None,
        instruction: str = "",
        query: str | None = None,
        max_depth: int = 3,
        max_files: int = 8,
        max_tokens: int = 8000,
    ) -> dict[str, Any]:
        """Scan *path*, navigate the dependency graph and compose an
        LLM-ready prompt.

        Every file is parsed with :class:`ASTManager` and each import is
        resolved to a real file path via :func:`_resolve_import_to_path`
        (absolute imports, ``from pkg import submodule``, and relative
        imports such as ``from . import X`` / ``from ..pkg import Y``,
        including package ``__init__.py`` targets), so the
        :class:`ContextBuilder` BFS walks actual files — dependencies AND
        dependents. Imports of stdlib/third-party modules are skipped.

        When *seed_files* is ``None``, entry points (files that nothing
        imports) are used as seeds. When *query* is provided, the BFS
        selection is **re-ranked by symbol relevance** (see
        :func:`_rank_selection`): files defining the symbols matched by
        *query* come first in the injected prompt, seeds staying at the
        top. Returns the selection (with depths/tokens and per-file
        ``relevance``/``matched_symbols`` when ranked), the final prompt
        and its estimated token count.
        """
        files = await self.scan_project(path)
        files_by_path = {file.path: file.content for file in files}

        index = SymbolIndex()
        index.index_files(files)

        # Resolve imports (absolute + relative) to real file paths for BFS.
        module_map = _module_to_path_map(files, path)
        root_path = Path(path).resolve()
        nav_graph = DependencyGraph()
        ast_manager = ASTManager()
        for file in files:
            try:
                rel = Path(file.path).resolve().relative_to(root_path)
            except ValueError:
                continue
            parsed = ast_manager.parse(file.content or "")
            if parsed is None:
                continue
            for imp in parsed.get("imports", []):
                resolved = _resolve_import_to_path(rel, imp, module_map)
                if resolved is not None and resolved != file.path:
                    nav_graph.add(file.path, resolved)

        if seed_files is None:
            seeds = [node for node in nav_graph.nodes()
                     if not nav_graph.get_dependents(node)]
            seeds = seeds or (nav_graph.nodes()[:1] if nav_graph.nodes() else [])
        else:
            seeds = list(seed_files)

        context = ContextBuilder(max_depth=max_depth,
                                 max_files=max_files,
                                 max_tokens=max_tokens)
        selection = context.build(seeds, nav_graph, files_by_path)
        ranked = _rank_selection(selection["selected"], index, query)
        selection["selected"] = ranked
        selection["files"] = [entry["path"] for entry in ranked]
        prompt_builder = PromptBuilder(max_tokens=max_tokens)
        prompt = prompt_builder.build_from_selection(
            instruction, ranked, files_by_path
        )
        prompt_tokens = prompt_builder.tokens(prompt)
        return {
            "path": path,
            "files": len(files),
            "symbols": index.count(),
            "graph_nodes": len(nav_graph.nodes()),
            "graph_edges": len(nav_graph.edges()),
            "seed_files": seeds,
            "query": query,
            "selection": selection,
            "prompt": prompt,
            "prompt_tokens": prompt_tokens,
            "fits_budget": prompt_tokens <= max_tokens,
        }

    # -- LLM execution (build_llm_context -> LLMEngine) ---------------------

    @property
    def llm(self) -> LLMEngine:
        """Lazily-instantiated :class:`ai.llm.LLMEngine`.

        Imported on first access so the heavy ``ai.llm`` package is not
        loaded unless the engine actually sends prompts.
        """
        if self._llm is None:
            from ai.llm import LLMEngine

            self._llm = LLMEngine()
        return self._llm

    async def ask_llm(
        self,
        path: str,
        seed_files: list[str] | None = None,
        instruction: str = "",
        query: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        llm: LLMEngine | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send an anchored LLM prompt built from *path* and return the reply.

        Composes :meth:`build_llm_context` (scan -> SymbolIndex ->
        DependencyGraph -> BFS selection -> relevance-ranked prompt) with
        :class:`ai.llm.LLMEngine`: the assembled prompt is executed against
        the chosen *provider* (or auto-routed) and the response is returned
        together with the anchored file selection.

        When *llm* is ``None`` an engine is created lazily and providers are
        auto-registered from environment variables; if no provider is
        available — or the routed provider returns an empty reply (e.g.
        missing/expired API key) — a :class:`MockProvider` is used so the
        call always returns an anchored answer (``mode`` is ``"mock"`` in
        that case).
        """
        context = await self.build_llm_context(
            path, seed_files=seed_files, instruction=instruction, query=query,
        )
        prompt = context["prompt"]
        prompt_tokens = context["prompt_tokens"]

        engine = llm or self.llm
        mode = "real"
        if provider is None and not engine.manager.registered_providers:
            await engine.manager.auto_register_providers()
            if not engine.manager.registered_providers:
                from ai.llm import MockProvider

                engine.manager.registry.register(MockProvider())
                mode = "mock"

        response = await engine.execute(
            prompt=prompt,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        if provider is None and not (response.content or "").strip():
            # The routed provider returned nothing (missing/expired API key,
            # no network, auth failure). Degrade gracefully to the mock so
            # the pipeline still returns an anchored reply.
            from ai.llm import MockProvider

            if engine.manager.registry.get("mock") is None:
                engine.manager.registry.register(MockProvider())
            mode = "mock"
            response = await engine.execute(
                prompt=prompt,
                provider="mock",
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

        return {
            "prompt": prompt,
            "prompt_tokens": prompt_tokens,
            "anchored_files": context["selection"]["selected"],
            "response": {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "tokens_prompt": response.tokens_prompt,
                "tokens_completion": response.tokens_completion,
                "latency_ms": response.latency_ms,
                "cost_usd": response.cost_usd,
                "finish_reason": response.finish_reason,
            },
            "mode": mode,
        }
