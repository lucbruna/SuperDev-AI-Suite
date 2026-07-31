"""Comprehensive tests for customer_experience subsystem (Volume 34)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer_experience.cx_config import CXConfig, CXConfigEntry
from customer_experience.cx_context import CXContext
from customer_experience.cx_engine import CXEngine
from customer_experience.cx_events import CXEventBus, CXEventType
from customer_experience.cx_factory import CXFactory
from customer_experience.cx_logger import CXLogger, CXLogLevel
from customer_experience.cx_manager import CXManager
from customer_experience.cx_metrics import CXMetrics
from customer_experience.cx_models import (
    Customer,
    CustomerJourney,
    CustomerProfile,
    CustomerStatus,
    CustomerTier,
    Interaction,
    InteractionType,
    Lead,
    LeadStatus,
    LoyaltyAction,
    LoyaltyTransaction,
    Recommendation,
    SentimentType,
    Ticket,
    TicketPriority,
    TicketStatus,
)
from customer_experience.cx_protocols import CXProtocols, CXProtocolType
from customer_experience.cx_registry import CXRegistry
from customer_experience.cx_runtime import CXRuntime, CXTaskState
from customer_experience.cx_security import CXSecurity, CXSecurityCheck, CXSeverity
from customer_experience.journey.models import JourneyStage


class TestCXModels(unittest.TestCase):
    def test_customer_status(self):
        self.assertEqual(CustomerStatus.ACTIVE.value, "active")
        self.assertEqual(CustomerStatus.CHURNED.value, "churned")

    def test_customer_tier(self):
        self.assertEqual(CustomerTier.BRONZE.value, "bronze")
        self.assertEqual(CustomerTier.DIAMOND.value, "diamond")

    def test_interaction_type(self):
        self.assertEqual(InteractionType.EMAIL.value, "email")
        self.assertEqual(InteractionType.CHAT.value, "chat")

    def test_ticket_priority(self):
        self.assertEqual(TicketPriority.LOW.value, "low")
        self.assertEqual(TicketPriority.URGENT.value, "urgent")

    def test_ticket_status(self):
        self.assertEqual(TicketStatus.OPEN.value, "open")
        self.assertEqual(TicketStatus.RESOLVED.value, "resolved")

    def test_sentiment_type(self):
        self.assertEqual(SentimentType.POSITIVE.value, "positive")
        self.assertEqual(SentimentType.NEGATIVE.value, "negative")

    def test_lead_status(self):
        self.assertEqual(LeadStatus.NEW.value, "new")
        self.assertEqual(LeadStatus.WON.value, "won")

    def test_loyalty_action(self):
        self.assertEqual(LoyaltyAction.EARN.value, "earn")
        self.assertEqual(LoyaltyAction.REDEEM.value, "redeem")

    def test_customer(self):
        c = Customer(customer_id="c1", name="Joao", email="j@test.com")
        self.assertEqual(c.name, "Joao")
        self.assertEqual(c.status, CustomerStatus.ACTIVE)

    def test_customer_profile(self):
        p = CustomerProfile(customer_id="c1", segment="premium", behavior_score=0.85)
        self.assertEqual(p.segment, "premium")

    def test_interaction(self):
        i = Interaction(interaction_id="i1", customer_id="c1", content="Hello")
        self.assertEqual(i.content, "Hello")

    def test_ticket(self):
        t = Ticket(ticket_id="t1", customer_id="c1", subject="Issue")
        self.assertEqual(t.status, TicketStatus.OPEN)

    def test_lead(self):
        l = Lead(lead_id="l1", name="Lead1", score=75.0)
        self.assertEqual(l.score, 75.0)

    def test_recommendation(self):
        r = Recommendation(recommendation_id="r1", customer_id="c1", item_name="Product A")
        self.assertEqual(r.item_name, "Product A")

    def test_loyalty_transaction(self):
        lt = LoyaltyTransaction(transaction_id="t1", customer_id="c1", points=100)
        self.assertEqual(lt.points, 100)

    def test_journey_stage(self):
        self.assertEqual(JourneyStage.AWARENESS.value, "awareness")
        self.assertEqual(JourneyStage.ADVOCACY.value, "advocacy")

    def test_customer_journey(self):
        j = CustomerJourney(journey_id="j1", customer_id="c1")
        self.assertEqual(j.current_stage, "")


class TestCXConfig(unittest.TestCase):
    def test_config_entry(self):
        e = CXConfigEntry(key="k", value="v")
        self.assertEqual(e.key, "k")

    def test_config_set_get(self):
        c = CXConfig()
        c.set("debug", True)
        self.assertTrue(c.get("debug"))

    def test_config_defaults(self):
        c = CXConfig()
        self.assertTrue(c.enabled)
        self.assertTrue(c.chatbot_enabled)


class TestCXEngine(unittest.TestCase):
    def test_add_customer(self):
        e = CXEngine()
        c = Customer(customer_id="c1", name="Test")
        e.add_customer(c)
        self.assertIsNotNone(e.get_customer("c1"))

    def test_update_customer(self):
        e = CXEngine()
        e.add_customer(Customer(customer_id="c1", name="Old"))
        e.update_customer("c1", {"name": "New"})
        self.assertEqual(e.get_customer("c1").name, "New")

    def test_search_customers(self):
        e = CXEngine()
        e.add_customer(Customer(customer_id="c1", name="Joao Silva"))
        e.add_customer(Customer(customer_id="c2", name="Maria Santos"))
        results = e.search_customers("joao")
        self.assertEqual(len(results), 1)

    def test_add_interaction(self):
        e = CXEngine()
        i = Interaction(interaction_id="i1", customer_id="c1")
        e.add_interaction(i)
        self.assertEqual(len(e.get_customer_interactions("c1")), 1)

    def test_add_ticket(self):
        e = CXEngine()
        t = Ticket(ticket_id="t1", customer_id="c1")
        e.add_ticket(t)
        self.assertEqual(len(e.get_tickets()), 1)

    def test_add_lead(self):
        e = CXEngine()
        l = Lead(lead_id="l1", name="Lead")
        e.add_lead(l)
        self.assertEqual(len(e.get_leads()), 1)

    def test_stats(self):
        e = CXEngine()
        e.add_customer(Customer(customer_id="c1", name="A"))
        stats = e.get_stats()
        self.assertEqual(stats["customers"], 1)


class TestCXManager(unittest.TestCase):
    def test_create_project(self):
        m = CXManager()
        p = m.create_project("Test")
        self.assertIsNotNone(p.project_id)

    def test_list_projects(self):
        m = CXManager()
        m.create_project("A")
        m.create_project("B")
        self.assertEqual(len(m.list_projects()), 2)

    def test_add_artifact(self):
        m = CXManager()
        p = m.create_project("Test")
        a = m.add_artifact(p.project_id, "report", {"title": "Q1"})
        self.assertEqual(a["type"], "report")

    def test_approve(self):
        m = CXManager()
        p = m.create_project("Test")
        self.assertTrue(m.approve(p.project_id, "admin"))


class TestCXFactory(unittest.TestCase):
    def test_create_customer(self):
        f = CXFactory()
        c = f.create_customer("Joao", email="j@test.com")
        self.assertEqual(c.name, "Joao")

    def test_create_from_template(self):
        f = CXFactory()
        c = f.create_customer_from_template("vip_customer", "VIP Corp")
        self.assertEqual(c.tier, CustomerTier.PLATINUM)

    def test_create_interaction(self):
        f = CXFactory()
        i = f.create_interaction("c1", InteractionType.PHONE)
        self.assertEqual(i.interaction_type, InteractionType.PHONE)

    def test_create_ticket(self):
        f = CXFactory()
        t = f.create_ticket("c1", "Bug report", TicketPriority.HIGH)
        self.assertEqual(t.priority, TicketPriority.HIGH)

    def test_create_lead(self):
        f = CXFactory()
        l = f.create_lead("Lead", email="l@test.com", source="website")
        self.assertEqual(l.source, "website")

    def test_templates(self):
        f = CXFactory()
        self.assertIn("vip_customer", f.list_templates())


class TestCXRegistry(unittest.TestCase):
    def test_register(self):
        r = CXRegistry()
        c = r.register("c1", "CRM", component_type="engine")
        self.assertEqual(c.name, "CRM")

    def test_get(self):
        r = CXRegistry()
        r.register("c1", "A")
        self.assertIsNotNone(r.get("c1"))

    def test_deregister(self):
        r = CXRegistry()
        r.register("c1", "A")
        self.assertTrue(r.deregister("c1"))
        self.assertIsNone(r.get("c1"))

    def test_get_by_type(self):
        r = CXRegistry()
        r.register("c1", "A", component_type="engine")
        r.register("c2", "B", component_type="dashboard")
        self.assertEqual(len(r.get_by_type("engine")), 1)

    def test_dependencies(self):
        r = CXRegistry()
        r.register("c1", "A")
        r.register("c2", "B")
        r.add_dependency("c1", "c2")
        self.assertEqual(r.get_dependencies("c1"), ["c2"])


class TestCXRuntime(unittest.TestCase):
    def test_submit_task(self):
        rt = CXRuntime()
        t = rt.submit_task("p1", "Task1")
        self.assertIsNotNone(t.task_id)

    def test_execute_task(self):
        rt = CXRuntime()
        t = rt.submit_task("p1", "Task1")
        self.assertTrue(rt.execute_task(t.task_id))

    def test_execute_with_handler(self):
        rt = CXRuntime()
        rt.register_handler("custom", lambda x: {"result": "done"})
        t = rt.submit_task("p1", "custom")
        self.assertTrue(rt.execute_task(t.task_id))
        self.assertEqual(t.output_data["result"], "done")

    def test_cancel_task(self):
        rt = CXRuntime()
        t = rt.submit_task("p1", "Task1")
        self.assertTrue(rt.cancel_task(t.task_id))

    def test_task_states(self):
        self.assertEqual(CXTaskState.PENDING.value, "pending")
        self.assertEqual(CXTaskState.COMPLETED.value, "completed")


class TestCXContext(unittest.TestCase):
    def test_set_get(self):
        ctx = CXContext()
        ctx.set("key1", "val1")
        self.assertEqual(ctx.get("key1"), "val1")

    def test_delete(self):
        ctx = CXContext()
        ctx.set("key1", "val1")
        self.assertTrue(ctx.delete("key1"))
        self.assertIsNone(ctx.get("key1"))

    def test_get_all(self):
        ctx = CXContext()
        ctx.set("a", 1)
        ctx.set("b", 2)
        self.assertEqual(len(ctx.get_all()), 2)

    def test_count(self):
        ctx = CXContext()
        ctx.set("a", 1)
        self.assertEqual(ctx.count(), 1)


class TestCXEvents(unittest.TestCase):
    def test_event_types(self):
        self.assertEqual(CXEventType.CUSTOMER_CREATED.value, "customer_created")
        self.assertEqual(CXEventType.TICKET_RESOLVED.value, "ticket_resolved")

    def test_publish(self):
        bus = CXEventBus()
        evt = bus.publish(CXEventType.CUSTOMER_CREATED, "crm")
        self.assertIsNotNone(evt.event_id)

    def test_subscribe(self):
        bus = CXEventBus()
        received = []
        bus.subscribe(CXEventType.CUSTOMER_CREATED, lambda e: received.append(e))
        bus.publish(CXEventType.CUSTOMER_CREATED, "src")
        self.assertEqual(len(received), 1)

    def test_get_events(self):
        bus = CXEventBus()
        bus.publish(CXEventType.CUSTOMER_CREATED, "src1")
        bus.publish(CXEventType.TICKET_CREATED, "src2")
        events = bus.get_events(event_type=CXEventType.CUSTOMER_CREATED)
        self.assertEqual(len(events), 1)


class TestCXMetrics(unittest.TestCase):
    def test_record(self):
        m = CXMetrics()
        p = m.record("response_time", 150.0)
        self.assertEqual(p.value, 150.0)

    def test_summary(self):
        m = CXMetrics()
        m.record("rt", 100.0)
        m.record("rt", 200.0)
        s = m.get_summary("rt")
        self.assertEqual(s.count, 2)
        self.assertAlmostEqual(s.avg_val, 150.0)

    def test_get_all(self):
        m = CXMetrics()
        m.record("a", 1.0)
        m.record("b", 2.0)
        self.assertEqual(len(m.get_all_metrics()), 2)


class TestCXLogger(unittest.TestCase):
    def test_log_levels(self):
        self.assertEqual(CXLogLevel.INFO.value, "info")
        self.assertEqual(CXLogLevel.ERROR.value, "error")

    def test_info(self):
        l = CXLogger()
        e = l.info("test")
        self.assertEqual(e.message, "test")

    def test_error(self):
        l = CXLogger()
        e = l.error("err")
        self.assertEqual(e.level, CXLogLevel.ERROR)

    def test_get_entries(self):
        l = CXLogger()
        l.info("a")
        l.error("b")
        self.assertEqual(len(l.get_entries()), 2)

    def test_filter_level(self):
        l = CXLogger()
        l.info("a")
        l.error("b")
        self.assertEqual(len(l.get_entries(level=CXLogLevel.ERROR)), 1)

    def test_count(self):
        l = CXLogger()
        l.info("a")
        self.assertEqual(l.count(), 1)


class TestCXProtocols(unittest.TestCase):
    def test_register(self):
        p = CXProtocols()
        c = p.register("api", CXProtocolType.REST)
        self.assertEqual(c.name, "api")

    def test_get(self):
        p = CXProtocols()
        p.register("api", CXProtocolType.REST)
        self.assertIsNotNone(p.get("api"))

    def test_deregister(self):
        p = CXProtocols()
        p.register("api", CXProtocolType.REST)
        self.assertTrue(p.deregister("api"))

    def test_count(self):
        p = CXProtocols()
        p.register("a", CXProtocolType.REST)
        self.assertEqual(p.count(), 1)


class TestCXSecurity(unittest.TestCase):
    def test_report_issue(self):
        s = CXSecurity()
        issue = s.report_issue(CXSecurityCheck.PRIVACY, CXSeverity.HIGH, "test")
        self.assertIsNotNone(issue.issue_id)

    def test_resolve(self):
        s = CXSecurity()
        issue = s.report_issue(CXSecurityCheck.AUDIT, CXSeverity.LOW)
        self.assertTrue(s.resolve_issue(issue.issue_id))
        self.assertTrue(issue.resolved)

    def test_get_issues(self):
        s = CXSecurity()
        s.report_issue(CXSecurityCheck.AUDIT, CXSeverity.LOW)
        s.report_issue(CXSecurityCheck.ENCRYPTION, CXSeverity.HIGH)
        self.assertEqual(len(s.get_issues()), 2)

    def test_score(self):
        s = CXSecurity()
        self.assertEqual(s.get_score(), 100.0)
        s.report_issue(CXSecurityCheck.LGPD, CXSeverity.CRITICAL)
        self.assertEqual(s.get_score(), 95.0)

    def test_policies(self):
        s = CXSecurity()
        s.create_policy("lgpd", {"encrypt": True})
        self.assertIn("lgpd", s.policies)


if __name__ == "__main__":
    unittest.main()
