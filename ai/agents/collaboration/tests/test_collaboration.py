from __future__ import annotations

from ..collaboration_engine import CollaborationEngine
from ..shared_context import SharedContext
from ..shared_memory import SharedMemory
from ..negotiation import Negotiation
from ..planning_board import PlanningBoard
from ..voting import Voting
from ..review_cycle import ReviewCycle
from ..approval import Approval
from ..feedback import Feedback


class TestSharedContext:
    def test_set_get(self) -> None:
        sc = SharedContext()
        sc.set("key", "value")
        assert sc.get("key") == "value"

    def test_remove(self) -> None:
        sc = SharedContext()
        sc.set("k", "v")
        assert sc.remove("k") is True


class TestSharedMemory:
    def test_store_retrieve(self) -> None:
        sm = SharedMemory()
        sm.store("k", "v")
        assert sm.retrieve("k") == "v"

    def test_delete(self) -> None:
        sm = SharedMemory()
        sm.store("k", "v")
        assert sm.delete("k") is True


class TestNegotiation:
    def test_propose_accept(self) -> None:
        n = Negotiation()
        n.propose("p1", "a1", {"share": "data"})
        assert n.accept("p1") is True

    def test_reject(self) -> None:
        n = Negotiation()
        n.propose("p1", "a1", {})
        assert n.reject("p1") is True


class TestPlanningBoard:
    def test_add_item(self) -> None:
        pb = PlanningBoard()
        pb.add_item("i1", "task")
        assert pb.item_count == 1

    def test_update_status(self) -> None:
        pb = PlanningBoard()
        pb.add_item("i1", "task")
        assert pb.update_status("i1", "done") is True

    def test_list_items(self) -> None:
        pb = PlanningBoard()
        pb.add_item("i1", "task")
        assert len(pb.list_items()) == 1


class TestVoting:
    def test_tally(self) -> None:
        v = Voting()
        v.cast("a1", "color", "red")
        v.cast("a2", "color", "red")
        v.cast("a3", "color", "blue")
        assert v.winner("color") == "red"


class TestReviewCycle:
    def test_start_review(self) -> None:
        rc = ReviewCycle()
        rc.start_review("r1", "code", ["a1", "a2"])
        assert rc.get_review("r1") is not None

    def test_approve(self) -> None:
        rc = ReviewCycle()
        rc.start_review("r1", "code", ["a1"])
        assert rc.approve("r1") is True


class TestApproval:
    def test_request_approve(self) -> None:
        a = Approval()
        a.request("req1", "a1", "deploy", "ready")
        assert a.approve("req1") is True

    def test_deny(self) -> None:
        a = Approval()
        a.request("req1", "a1", "deploy", "ready")
        assert a.deny("req1") is True


class TestFeedback:
    def test_give_get(self) -> None:
        f = Feedback()
        f.give("a1", "a2", 4.5, "good")
        assert len(f.get_feedback("a1")) == 1

    def test_average_rating(self) -> None:
        f = Feedback()
        f.give("a1", "a2", 4.0)
        f.give("a1", "a3", 5.0)
        assert f.average_rating("a1") == 4.5


class TestCollaborationEngine:
    def test_get_status(self) -> None:
        ce = CollaborationEngine()
        s = ce.get_status()
        assert "context_keys" in s
