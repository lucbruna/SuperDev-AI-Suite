from __future__ import annotations

from ..arbitration import Arbitration
from ..conflict_resolution import ConflictResolution
from ..consensus import Consensus
from ..coordinator import Coordinator
from ..dependency_manager import DependencyManager
from ..leader_election import LeaderElection
from ..load_balancer import LoadBalancer
from ..priority_manager import PriorityManager
from ..synchronization import Synchronization
from ..task_allocator import TaskAllocator
from ..team_manager import TeamManager


class TestTeamManager:
    def test_create_team(self) -> None:
        tm = TeamManager()
        tm.create_team("team_a")
        assert "team_a" in tm.list_teams()

    def test_add_remove_member(self) -> None:
        tm = TeamManager()
        tm.create_team("t1")
        assert tm.add_member("t1", "a1") is True
        assert tm.add_member("t1", "a1") is False  # duplicate
        assert len(tm.get_team("t1")) == 1
        assert tm.remove_member("t1", "a1") is True


class TestTaskAllocator:
    def test_assign(self) -> None:
        ta = TaskAllocator()
        agent = ta.assign({"id": "t1"}, ["a1", "a2"])
        assert agent in ("a1", "a2")

    def test_get_agent(self) -> None:
        ta = TaskAllocator()
        ta.assign({"id": "t1"}, ["a1"])
        assert ta.get_agent_for_task("t1") == "a1"


class TestLoadBalancer:
    def test_register_assign(self) -> None:
        lb = LoadBalancer()
        lb.register("a1")
        lb.register("a2")
        lb.assign("a1")
        assert lb.get_load("a1") == 1

    def test_least_loaded(self) -> None:
        lb = LoadBalancer()
        lb.register("a1")
        lb.register("a2")
        lb.assign("a1", 5)
        assert lb.get_least_loaded() == "a2"


class TestPriorityManager:
    def test_priorities(self) -> None:
        pm = PriorityManager()
        pm.set_priority("t1", 1)
        pm.set_priority("t2", 3)
        sorted_tasks = pm.sorted_tasks()
        assert sorted_tasks[0][0] == "t2"


class TestDependencyManager:
    def test_dependencies(self) -> None:
        dm = DependencyManager()
        dm.add_dependency("t2", "t1")
        assert dm.get_dependencies("t2") == ["t1"]
        assert not dm.is_ready("t2", ["t1"])
        assert dm.is_ready("t2", ["t1", "done"])


class TestConsensus:
    def test_vote_result(self) -> None:
        c = Consensus()
        c.vote("a1", "color", "red")
        c.vote("a2", "color", "red")
        c.vote("a3", "color", "blue")
        assert c.result("color") == "red"


class TestArbitration:
    def test_resolve(self) -> None:
        a = Arbitration()
        a.register_conflict("c1", "a1", "a2", "resource")
        assert a.resolve("c1", "grant_a1") is True
        assert a.resolved_count == 1


class TestLeaderElection:
    def test_elect(self) -> None:
        le = LeaderElection()
        le.nominate("a1")
        le.nominate("a2")
        leader = le.elect()
        assert leader == "a1"
        assert le.election_count == 1

    def test_step_down(self) -> None:
        le = LeaderElection()
        le.nominate("a1")
        le.elect()
        le.step_down()
        assert le.leader is None


class TestConflictResolution:
    def test_resolve(self) -> None:
        cr = ConflictResolution()
        cr.add_strategy("resource", "priority")
        result = cr.resolve("resource", {"agents": ["a1", "a2"]})
        assert "priority" in result


class TestSynchronization:
    def test_lock(self) -> None:
        s = Synchronization()
        assert s.acquire_lock("r1", "a1") is True
        assert s.acquire_lock("r1", "a2") is False
        assert s.release_lock("r1") is True

    def test_barrier(self) -> None:
        s = Synchronization()
        s.create_barrier("b1", 2)
        s.wait_barrier("b1", "a1")
        assert not s.barrier_ready("b1", 2)
        s.wait_barrier("b1", "a2")
        assert s.barrier_ready("b1", 2)


class TestCoordinator:
    def test_assign(self) -> None:
        c = Coordinator()
        c.team_manager.create_team("t1")
        c.team_manager.add_member("t1", "a1")
        agent = c.assign_task("t1", {"id": "task1"})
        assert agent == "a1"

    def test_get_status(self) -> None:
        c = Coordinator()
        s = c.get_status()
        assert "teams" in s
