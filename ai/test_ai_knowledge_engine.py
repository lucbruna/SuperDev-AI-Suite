"""Comprehensive tests for ai_knowledge_engine (Volume 40)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest

from ai_knowledge_engine import (
    ConfidenceLevel,
    Document,
    DocumentSubEngine,
    EmbeddingSubEngine,
    GraphSubEngine,
    Knowledge,
    KnowledgeConfig,
    KnowledgeContext,
    KnowledgeEngine,
    KnowledgeEvent,
    KnowledgeEventType,
    KnowledgeFactory,
    KnowledgeLogger,
    KnowledgeManager,
    KnowledgeMetrics,
    KnowledgeRegistry,
    KnowledgeRuntime,
    KnowledgeSecurity,
    KnowledgeType,
    LearningExperience,
    LearningSubEngine,
    ReasoningSubEngine,
    ResearchEngine,
    ResearchQuery,
    ResearchResult,
    ResearchSubEngine,
    SourceType,
    ValidationStatus,
    ValidationSubEngine,
    VectorSubEngine,
)


class TestKnowledgeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = KnowledgeEngine()

    def test_store_knowledge(self):
        kb = Knowledge(title="Test", content="Content", knowledge_type=KnowledgeType.FACT)
        result = self.engine.store_knowledge(kb)
        self.assertIsNotNone(result)
        self.assertIsNotNone(self.engine.get_knowledge(result.knowledge_id))

    def test_search_knowledge(self):
        self.engine.store_knowledge(Knowledge(title="Python", content="Programming language"))
        self.engine.store_knowledge(Knowledge(title="Java", content="Another language"))
        results = self.engine.search_knowledge("Python")
        self.assertEqual(len(results), 1)

    def test_update_knowledge(self):
        kb = self.engine.store_knowledge(Knowledge(title="Old", content="Old content"))
        self.assertTrue(self.engine.update_knowledge(kb.knowledge_id, content="New content"))
        updated = self.engine.get_knowledge(kb.knowledge_id)
        self.assertEqual(updated.content, "New content")
        self.assertEqual(updated.version, 2)

    def test_delete_knowledge(self):
        kb = self.engine.store_knowledge(Knowledge(title="Delete me"))
        self.assertTrue(self.engine.delete_knowledge(kb.knowledge_id))
        self.assertIsNone(self.engine.get_knowledge(kb.knowledge_id))

    def test_link_knowledge(self):
        kb1 = self.engine.store_knowledge(Knowledge(title="A"))
        kb2 = self.engine.store_knowledge(Knowledge(title="B"))
        self.assertTrue(self.engine.link_knowledge(kb1.knowledge_id, kb2.knowledge_id))
        related = self.engine.get_related_knowledge(kb1.knowledge_id)
        self.assertEqual(len(related), 1)

    def test_store_document(self):
        doc = Document(title="Doc1", content="Content")
        self.engine.store_document(doc)
        self.assertIsNotNone(self.engine.get_document(doc.document_id))

    def test_record_experience(self):
        exp = LearningExperience(title="Exp1", description="Test")
        self.engine.record_experience(exp)
        self.assertIsNotNone(self.engine.get_experience(exp.experience_id))

    def test_stats(self):
        self.engine.store_knowledge(Knowledge(title="K1"))
        stats = self.engine.get_stats()
        self.assertEqual(stats["total_knowledge"], 1)


class TestResearchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ResearchEngine()

    def test_create_query(self):
        query = self.engine.create_query("AI trends", "info", 10)
        self.assertIsNotNone(query)
        self.assertEqual(query.query_text, "AI trends")

    def test_add_result(self):
        result = ResearchResult(title="Result1", content="Content", relevance_score=0.9)
        self.engine.add_result(result)
        self.assertIsNotNone(self.engine.get_result(result.result_id))

    def test_register_source(self):
        self.engine.register_source("web", SourceType.WEB, {"url": "https://example.com"})
        source = self.engine.get_source("web")
        self.assertIsNotNone(source)

    def test_plan_research(self):
        plan = self.engine.plan_research("AI in healthcare", depth=3)
        self.assertEqual(plan["topic"], "AI in healthcare")
        self.assertEqual(len(plan["phases"]), 3)

    def test_score_relevance(self):
        query = ResearchQuery(query_text="machine learning")
        result = ResearchResult(title="Machine Learning Guide", content="Introduction to ML")
        score = self.engine.score_relevance(result, query)
        self.assertGreater(score, 0)

    def test_deduplicate(self):
        r1 = ResearchResult(title="Same", source=SourceType.WEB)
        r2 = ResearchResult(title="Same", source=SourceType.WEB)
        r3 = ResearchResult(title="Different", source=SourceType.WEB)
        unique = self.engine.deduplicate_results([r1, r2, r3])
        self.assertEqual(len(unique), 2)


class TestKnowledgeManager(unittest.TestCase):
    def setUp(self):
        self.manager = KnowledgeManager()

    def test_add_knowledge(self):
        kb = self.manager.add_knowledge("Title", "Content", "fact", "web", ["tag1"])
        self.assertIsNotNone(kb)
        self.assertEqual(kb.title, "Title")

    def test_find_knowledge(self):
        self.manager.add_knowledge("Python", "Language", "concept")
        results = self.manager.find_knowledge("Python")
        self.assertEqual(len(results), 1)

    def test_validate_knowledge(self):
        kb = self.manager.add_knowledge("Test", "Content")
        self.assertTrue(self.manager.validate_knowledge(kb.knowledge_id, ConfidenceLevel.HIGH))
        validated = self.manager.get_knowledge(kb.knowledge_id)
        self.assertEqual(validated.validation_status, ValidationStatus.VALIDATED)

    def test_link_concepts(self):
        kb1 = self.manager.add_knowledge("A", "Content A")
        kb2 = self.manager.add_knowledge("B", "Content B")
        self.assertTrue(self.manager.link_concepts(kb1.knowledge_id, kb2.knowledge_id))

    def test_get_by_type(self):
        self.manager.add_knowledge("Fact1", "Content", "fact")
        self.manager.add_knowledge("Insight1", "Content", "insight")
        facts = self.manager.get_by_type("fact")
        self.assertEqual(len(facts), 1)

    def test_get_top_knowledge(self):
        for i in range(5):
            self.manager.add_knowledge(f"K{i}", "Content")
        top = self.manager.get_top_knowledge(3)
        self.assertEqual(len(top), 3)


class TestResearchSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ResearchSubEngine()

    def test_start_session(self):
        session = self.engine.start_session("AI Research")
        self.assertIsNotNone(session)
        self.assertEqual(session.topic, "AI Research")

    def test_collect_information(self):
        session = self.engine.start_session("Test")
        info = self.engine.collect_information(session.session_id, "Finding1", "Content", relevance=0.8)
        self.assertIsNotNone(info)

    def test_advance_phase(self):
        session = self.engine.start_session("Test")
        self.assertTrue(self.engine.advance_phase(session.session_id))
        self.assertEqual(session.phase.value, "collection")

    def test_search_information(self):
        session = self.engine.start_session("Test")
        self.engine.collect_information(session.session_id, "Python", "Programming language")
        results = self.engine.search_information("Python")
        self.assertEqual(len(results), 1)

    def test_get_top_findings(self):
        session = self.engine.start_session("Test")
        self.engine.collect_information(session.session_id, "High", "Content", relevance=0.9)
        self.engine.collect_information(session.session_id, "Low", "Content", relevance=0.3)
        top = self.engine.get_top_findings(session.session_id, 1)
        self.assertEqual(top[0].title, "High")


class TestDocumentSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DocumentSubEngine()

    def test_process_document(self):
        doc = self.engine.process_document("Test Doc", "This is test content for processing")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.status.value, "completed")

    def test_summarize(self):
        doc = self.engine.process_document("Doc", "Sentence one. Sentence two. Sentence three. Sentence four.")
        summary = self.engine.summarize(doc.doc_id)
        self.assertGreater(len(summary), 0)

    def test_extract_information(self):
        doc = self.engine.process_document("Doc", "Author: John Smith. Date: 2024.")
        results = self.engine.extract_information(doc.doc_id, ["author", "date"])
        self.assertEqual(len(results), 2)

    def test_search_documents(self):
        self.engine.process_document("Python Guide", "Python is great")
        self.engine.process_document("Java Guide", "Java is popular")
        results = self.engine.search_documents("Python")
        self.assertEqual(len(results), 1)

    def test_chunking(self):
        engine = DocumentSubEngine(chunk_size=20, chunk_overlap=5)
        doc = engine.process_document("Long", "A" * 100)
        self.assertGreater(len(doc.chunks), 1)


class TestVectorSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = VectorSubEngine(dimensions=64)

    def test_store_and_get(self):
        entry = self.engine.store("Hello world")
        self.assertIsNotNone(entry)
        self.assertIsNotNone(self.engine.get(entry.entry_id))

    def test_search(self):
        self.engine.store("Python programming")
        self.engine.store("Java development")
        self.engine.store("Cooking recipes")
        results = self.engine.search("programming")
        self.assertGreater(len(results), 0)

    def test_delete(self):
        entry = self.engine.store("Delete me")
        self.assertTrue(self.engine.delete(entry.entry_id))
        self.assertIsNone(self.engine.get(entry.entry_id))

    def test_similarity_search(self):
        e1 = self.engine.store("machine learning")
        self.engine.store("deep learning")
        self.engine.store("cooking")
        similar = self.engine.get_similar(e1.entry_id, 2)
        self.assertEqual(len(similar), 2)

    def test_optimize(self):
        self.engine.store("test1")
        self.engine.store("test1")
        removed = self.engine.optimize()
        self.assertGreaterEqual(removed, 0)


class TestEmbeddingSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EmbeddingSubEngine(dimensions=64)

    def test_embed(self):
        emb = self.engine.embed("Hello world")
        self.assertIsNotNone(emb)
        self.assertEqual(len(emb.vector), 64)

    def test_batch_embed(self):
        embs = self.engine.batch_embed(["text1", "text2", "text3"])
        self.assertEqual(len(embs), 3)

    def test_similarity(self):
        score = self.engine.similarity("hello world", "hello world")
        self.assertAlmostEqual(score, 1.0, places=5)

    def test_find_similar(self):
        self.engine.embed("Python programming")
        self.engine.embed("Java development")
        results = self.engine.find_similar("programming", 2)
        self.assertGreater(len(results), 0)


class TestReasoningSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ReasoningSubEngine()

    def test_add_observation(self):
        obs = self.engine.add_observation("High CPU usage", {"cpu": 95})
        self.assertIsNotNone(obs)

    def test_hypothesis(self):
        hyp = self.engine.add_hypothesis("Memory leak causes high CPU")
        self.assertIsNotNone(hyp)
        self.assertEqual(hyp.status.value, "proposed")

    def test_add_evidence(self):
        hyp = self.engine.add_hypothesis("Test hypothesis")
        self.assertTrue(self.engine.add_evidence(hyp.hypothesis_id, "Evidence 1", True))
        self.assertTrue(self.engine.add_evidence(hyp.hypothesis_id, "Evidence 2", True))
        self.assertGreater(hyp.confidence, 0.5)

    def test_infer(self):
        self.engine.add_rule("high_cpu", {"cpu": "high"}, "Need optimization")
        results = self.engine.infer({"cpu": "high"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "Need optimization")

    def test_analyze_problem(self):
        self.engine.add_observation("Database slow", {"db": True})
        result = self.engine.analyze_problem("System is slow")
        self.assertIn("hypotheses_generated", result)


class TestLearningSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LearningSubEngine()

    def test_record_experience(self):
        exp = self.engine.record_experience(
            "Cache improved perf", "Added Redis cache", "success", "2x faster", ["Use caching"]
        )
        self.assertIsNotNone(exp)

    def test_add_feedback(self):
        fb = self.engine.add_feedback("user1", 0.9, "Great feature", "ui")
        self.assertIsNotNone(fb)

    def test_suggest_improvement(self):
        imp = self.engine.suggest_improvement("Optimize queries", "Use indexing", "performance", 8)
        self.assertIsNotNone(imp)
        self.assertEqual(imp.priority, 8)

    def test_implement_improvement(self):
        imp = self.engine.suggest_improvement("Fix bug", "Critical fix")
        self.assertTrue(self.engine.implement_improvement(imp.improvement_id))

    def test_analyze_patterns(self):
        self.engine.record_experience("E1", "Desc", "success")
        self.engine.record_experience("E2", "Desc", "success")
        patterns = self.engine.analyze_patterns()
        self.assertGreater(len(patterns), 0)

    def test_get_lessons(self):
        self.engine.record_experience("E1", "Desc", "success", lessons=["Use cache", "Optimize DB"])
        lessons = self.engine.get_lessons_learned()
        self.assertIn("Use cache", lessons)


class TestValidationSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ValidationSubEngine()

    def test_validate_content(self):
        check = self.engine.validate_content("Fact: Python is a language", "source_check")
        self.assertIsNotNone(check)
        self.assertEqual(check.result.value, "valid")

    def test_fact_check(self):
        fc = self.engine.fact_check("Python is a programming language")
        self.assertIsNotNone(fc)

    def test_add_source(self):
        source = self.engine.add_source("Wikipedia", "https://wikipedia.org", 0.9)
        self.assertIsNotNone(source)
        self.assertEqual(self.engine.check_source_reliability(source.source_id), 0.9)

    def test_cross_validate(self):
        self.engine.validate_content("Python is popular", "source_check")
        self.engine.validate_content("Python is a language", "source_check")
        result = self.engine.cross_validate("Python")
        self.assertIn("confidence", result)


class TestGraphSubEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GraphSubEngine()

    def test_add_entity(self):
        entity = self.engine.add_entity("Python", "technology")
        self.assertIsNotNone(entity)
        self.assertEqual(entity.name, "Python")

    def test_add_relationship(self):
        e1 = self.engine.add_entity("Python", "technology")
        e2 = self.engine.add_entity("Programming", "concept")
        rel = self.engine.add_relationship(e1.entity_id, e2.entity_id, "is_a")
        self.assertIsNotNone(rel)

    def test_get_neighbors(self):
        e1 = self.engine.add_entity("A", "concept")
        e2 = self.engine.add_entity("B", "concept")
        self.engine.add_relationship(e1.entity_id, e2.entity_id, "related")
        neighbors = self.engine.get_neighbors(e1.entity_id)
        self.assertEqual(len(neighbors), 1)

    def test_find_path(self):
        a = self.engine.add_entity("A", "concept")
        b = self.engine.add_entity("B", "concept")
        c = self.engine.add_entity("C", "concept")
        self.engine.add_relationship(a.entity_id, b.entity_id, "next")
        self.engine.add_relationship(b.entity_id, c.entity_id, "next")
        path = self.engine.find_path(a.entity_id, c.entity_id)
        self.assertIsNotNone(path)
        self.assertEqual(len(path.nodes), 3)

    def test_delete_entity(self):
        e = self.engine.add_entity("Delete", "concept")
        self.assertTrue(self.engine.delete_entity(e.entity_id))
        self.assertIsNone(self.engine.get_entity(e.entity_id))

    def test_get_subgraph(self):
        a = self.engine.add_entity("A", "concept")
        b = self.engine.add_entity("B", "concept")
        self.engine.add_relationship(a.entity_id, b.entity_id, "related")
        graph = self.engine.get_subgraph(a.entity_id, depth=1)
        self.assertEqual(len(graph["entities"]), 2)


class TestInfrastructure(unittest.TestCase):
    def test_config(self):
        config = KnowledgeConfig()
        self.assertIsNotNone(config)
        self.assertEqual(config.embedding_dimensions, 384)

    def test_factory(self):
        kb = KnowledgeFactory.create_knowledge("Title", "Content", "fact")
        self.assertIsNotNone(kb)
        doc = KnowledgeFactory.create_document("Doc", "Content")
        self.assertIsNotNone(doc)
        query = KnowledgeFactory.create_research_query("test query")
        self.assertIsNotNone(query)
        exp = KnowledgeFactory.create_experience("Exp", "Desc")
        self.assertIsNotNone(exp)
        emb = KnowledgeFactory.create_embedding("text")
        self.assertIsNotNone(emb)
        templates = KnowledgeFactory.templates()
        self.assertIn("technical", templates)

    def test_registry(self):
        reg = KnowledgeRegistry()
        reg.register("test", "component", "cat1")
        self.assertEqual(reg.get("test"), "component")
        self.assertTrue(reg.unregister("test"))
        self.assertIsNone(reg.get("test"))

    def test_runtime(self):
        rt = KnowledgeRuntime()
        rt.start()
        self.assertTrue(rt.is_running())
        task_id = rt.submit_task("Test task", "research")
        self.assertIsNotNone(task_id)
        rt.stop()
        self.assertFalse(rt.is_running())

    def test_context(self):
        ctx = KnowledgeContext(session_id="s1", user_id="u1")
        ctx.add_to_history("user", "Hello")
        ctx.set_topic("AI")
        self.assertEqual(len(ctx.conversation_history), 1)
        ctx.clear()
        self.assertEqual(len(ctx.conversation_history), 0)

    def test_events(self):
        event = KnowledgeEvent(event_type=KnowledgeEventType.KNOWLEDGE_STORED, source="test")
        self.assertIsNotNone(event)

    def test_metrics(self):
        m = KnowledgeMetrics()
        m.record_store()
        m.record_retrieval()
        m.record_query()
        stats = m.get_stats()
        self.assertEqual(stats["knowledge_stored"], 1)

    def test_logger(self):
        l = KnowledgeLogger()
        l.info("Test message")
        self.assertEqual(l.count, 1)
        l.clear()
        self.assertEqual(l.count, 0)

    def test_security(self):
        sec = KnowledgeSecurity()
        from ai_knowledge_engine.knowledge_security import AccessPermission, AccessPolicy

        policy = AccessPolicy(
            policy_id="p1",
            user_role="admin",
            resource_type="knowledge",
            permissions=[AccessPermission.READ, AccessPermission.WRITE],
        )
        sec.add_policy(policy)
        self.assertTrue(sec.check_access("admin", "knowledge", AccessPermission.READ))
        self.assertFalse(sec.check_access("viewer", "knowledge", AccessPermission.WRITE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
