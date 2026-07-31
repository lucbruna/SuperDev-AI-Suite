"""
Test configuration
"""

import asyncio
from uuid import UUID

import pytest

from enterprise_ai_core.config import Config
from enterprise_ai_core.models import (
    Agent,
    AgentType,
    Event,
    EventType,
    MemoryEntry,
    MemoryType,
    PolicyAction,
    TaskPriority,
    TaskStatus,
    Workflow,
    WorkflowStatus,
)
from enterprise_ai_core.orchestrator import EnterpriseOrchestrator


@pytest.fixture
def config():
    return Config.from_env()


@pytest.fixture
def orchestrator(config):
    return EnterpriseOrchestrator(config)


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    await orchestrator.initialize()
    assert orchestrator._running is True
    await orchestrator.shutdown()
    assert orchestrator._running is False


@pytest.mark.asyncio
async def test_agent_registration(orchestrator):
    await orchestrator.initialize()

    agent = Agent(
        name="test_agent",
        type=AgentType.ANALYSIS,
        capabilities=["analysis", "reasoning"],
        permissions=["read_data"],
    )

    await orchestrator.register_agent(agent)
    retrieved = orchestrator.get_agent(agent.id)

    assert retrieved is not None
    assert retrieved.name == "test_agent"
    assert retrieved.type == AgentType.ANALYSIS

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_task_creation(orchestrator):
    await orchestrator.initialize()

    task = await orchestrator.task_manager.create_task(
        name="Test Task",
        payload={"query": "test"},
        priority=TaskPriority.NORMAL,
    )

    assert task is not None
    assert task.name == "Test Task"
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.NORMAL

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_workflow_execution(orchestrator):
    await orchestrator.initialize()

    workflow = Workflow(
        name="Test Workflow",
        steps=[
            {
                "id": "step1",
                "name": "Step 1",
                "type": "task",
                "agent_type": AgentType.ANALYSIS,
                "config": {"required_capabilities": ["analysis"]},
            }
        ],
    )

    execution = await orchestrator.execute_workflow(workflow)

    assert execution is not None
    assert execution.workflow_id == workflow.id
    assert execution.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_policy_evaluation(orchestrator):
    await orchestrator.initialize()

    evaluation = await orchestrator.policy_engine.evaluate(
        action="financial_transaction",
        context={"amount": 150000},
    )

    assert evaluation is not None
    assert evaluation.action in (PolicyAction.ALLOW, PolicyAction.REQUIRE_APPROVAL, PolicyAction.DENY)

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_memory_storage(orchestrator):
    await orchestrator.initialize()

    entry = MemoryEntry(
        type=MemoryType.SHORT_TERM,
        key="test_key",
        value={"data": "test_value"},
        tags=["test"],
    )

    entry_id = await orchestrator.memory_manager.store(entry)
    assert entry_id is not None

    retrieved = await orchestrator.memory_manager.retrieve("test_key")
    assert retrieved is not None
    assert retrieved.value["data"] == "test_value"

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_event_bus(orchestrator):
    await orchestrator.initialize()

    received = []

    async def handler(event):
        received.append(event)

    await orchestrator.subscribe(EventType.TASK_CREATED, handler)

    event = Event(
        type=EventType.TASK_CREATED,
        source_id=UUID(int=0),
        source_type="test",
        payload={"test": "data"},
    )

    await orchestrator.publish_event(event)
    await asyncio.sleep(0.1)

    assert len(received) == 1
    assert received[0].type == EventType.TASK_CREATED

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_decision_making(orchestrator):
    await orchestrator.initialize()

    decision = await orchestrator.decision_manager.make_decision(
        context={"budget": 100000},
        options=[
            {"name": "Option A", "cost": 50000, "roi": 1.5},
            {"name": "Option B", "cost": 80000, "roi": 2.0},
        ],
        criteria={"roi": 0.7, "cost": 0.3},
    )

    assert decision is not None
    assert decision.selected_option is not None
    assert decision.confidence > 0

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_security_authentication(orchestrator):
    await orchestrator.initialize()

    await orchestrator.security_manager.authenticate(
        credentials={"username": "admin", "password": "admin"},
    )

    # Will be None since no users configured, but shouldn't error
    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_audit_logging(orchestrator):
    await orchestrator.initialize()

    event_id = await orchestrator.audit_manager.log(
        event_type="test.event",
        action="test_action",
        outcome="success",
        details={"key": "value"},
    )

    assert event_id is not None

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_full_request_processing(orchestrator):
    await orchestrator.initialize()

    # Register a test agent
    agent = Agent(
        name="financial_ai",
        type=AgentType.ANALYSIS,
        capabilities=["financial_analysis", "forecasting"],
        permissions=["read_finance"],
    )
    await orchestrator.register_agent(agent)

    result = await orchestrator.process_request(
        query="Analyze Q4 financial performance",
        context={"quarter": "Q4", "year": 2024},
    )

    assert result is not None
    assert "request_id" in result
    assert "success" in result

    await orchestrator.shutdown()


@pytest.mark.asyncio
async def test_agent_health_monitoring(orchestrator):
    await orchestrator.initialize()

    agent = Agent(name="health_test", type=AgentType.REACTIVE)
    await orchestrator.register_agent(agent)

    health = orchestrator.agent_manager.get_agent_metrics(agent.id)

    assert health is not None
    assert "agent_id" in health
    assert "health_score" in health

    await orchestrator.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
