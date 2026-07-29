"""
Enterprise Orchestrator - Central brain for AI agent coordination
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from enterprise_ai_core.config import Config
from enterprise_ai_core.models import (
    Agent,
    AgentStatus,
    AgentType,
    Decision,
    Event,
    EventType,
    MemoryEntry,
    MemoryType,
    Task,
    TaskPriority,
    TaskStatus,
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
)
from enterprise_ai_core.agent_manager import AgentManager
from enterprise_ai_core.task_manager import TaskManager
from enterprise_ai_core.workflow_engine import WorkflowEngine
from enterprise_ai_core.governance_engine import GovernanceEngine
from enterprise_ai_core.memory_manager import MemoryManager
from enterprise_ai_core.event_bus import EventBus
from enterprise_ai_core.security_manager import SecurityManager
from enterprise_ai_core.audit_manager import AuditManager
from enterprise_ai_core.policy_engine import PolicyEngine
from enterprise_ai_core.decision_manager import DecisionManager


class EnterpriseOrchestrator:
    """
    Central orchestrator for enterprise AI agents.
    Coordinates agents, manages tasks, executes workflows, and enforces governance.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.id = uuid4()
        self.created_at = datetime.utcnow()

        self.agent_manager = AgentManager(self)
        self.task_manager = TaskManager(self)
        self.workflow_engine = WorkflowEngine(self)
        self.policy_engine = PolicyEngine(self)
        self.audit_manager = AuditManager(self)
        self.governance_engine = GovernanceEngine(self)
        self.memory_manager = MemoryManager(self)
        self.event_bus = EventBus(self)
        self.security_manager = SecurityManager(self)
        self.decision_manager = DecisionManager(self)

        self._running = False
        self._tasks: Dict[UUID, Task] = {}
        self._workflows: Dict[UUID, Workflow] = {}
        self._workflow_executions: Dict[UUID, WorkflowExecution] = {}
        self._active_agents: Set[UUID] = set()

    async def initialize(self) -> None:
        """Initialize all subsystems"""
        await self.event_bus.start()
        await self.agent_manager.initialize()
        await self.task_manager.initialize()
        await self.workflow_engine.initialize()
        await self.policy_engine.initialize()
        await self.governance_engine.initialize()
        await self.memory_manager.initialize()
        await self.security_manager.initialize()
        await self.audit_manager.initialize()
        await self.decision_manager.initialize()
        self._running = True

    async def shutdown(self) -> None:
        """Gracefully shutdown all subsystems"""
        self._running = False
        await self.decision_manager.shutdown()
        await self.policy_engine.shutdown()
        await self.audit_manager.shutdown()
        await self.security_manager.shutdown()
        await self.memory_manager.shutdown()
        await self.governance_engine.shutdown()
        await self.workflow_engine.shutdown()
        await self.task_manager.shutdown()
        await self.agent_manager.shutdown()
        await self.event_bus.stop()

    async def process_request(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        security_context: Optional[Dict] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> Dict[str, Any]:
        """
        Main entry point for processing user requests.
        Analyzes intent, selects agents, executes tasks, and consolidates responses.
        """
        request_id = uuid4()
        context = context or {}
        security_context = security_context or {}

        await self.audit_manager.log(
            event_type="request.received",
            action="process_request",
            details={
                "request_id": str(request_id),
                "query": query,
                "priority": priority.name,
            },
        )

        try:
            intent = await self._analyze_intent(query, context)

            agents = await self.agent_manager.select_agents(intent, context)

            if not agents:
                return {
                    "success": False,
                    "error": "No suitable agents found for request",
                    "request_id": str(request_id),
                }

            task = await self.task_manager.create_task(
                name=f"Process: {query[:50]}",
                description=query,
                agent_id=agents[0].id if agents else None,
                priority=priority,
                input_data={"query": query, "context": context, "intent": intent},
            )

            results = await self._execute_agents(agents, task, context)

            consolidated = await self._consolidate_results(results, intent, context)

            await self.memory_manager.store(
                MemoryEntry(
                    type=MemoryType.EPISODIC,
                    key=f"request_{request_id}",
                    value={
                        "query": query,
                        "context": context,
                        "intent": intent,
                        "results": results,
                        "consolidated": consolidated,
                    },
                    tags=["request", "processed"],
                )
            )

            await self.audit_manager.log(
                event_type="request.completed",
                action="process_request",
                outcome="success",
                details={"request_id": str(request_id), "agents_used": len(agents)},
            )

            return {
                "success": True,
                "request_id": str(request_id),
                "intent": intent,
                "agents_used": [a.name for a in agents],
                "results": results,
                "consolidated_response": consolidated,
            }

        except Exception as e:
            await self.audit_manager.log(
                event_type="request.failed",
                action="process_request",
                outcome="failure",
                details={"request_id": str(request_id), "error": str(e)},
                severity="error",
            )
            return {
                "success": False,
                "error": str(e),
                "request_id": str(request_id),
            }

    async def _analyze_intent(self, query: str, context: Dict) -> Dict[str, Any]:
        """Analyze user query to determine intent and required capabilities"""
        return {
            "query": query,
            "type": "analysis",
            "required_capabilities": ["analysis", "reasoning"],
            "domain": self._detect_domain(query),
            "complexity": self._estimate_complexity(query),
            "requires_consensus": self._requires_consensus(query),
        }

    def _detect_domain(self, query: str) -> str:
        query_lower = query.lower()
        domains = {
            "finance": ["finance", "budget", "revenue", "cost", "investment", "financial"],
            "legal": ["legal", "contract", "compliance", "regulation", "law"],
            "hr": ["hr", "human resource", "employee", "hiring", "payroll"],
            "marketing": ["marketing", "campaign", "brand", "customer", "advertising"],
            "operations": ["operations", "supply", "logistics", "inventory", "procurement"],
            "security": ["security", "threat", "vulnerability", "breach", "access"],
        }
        for domain, keywords in domains.items():
            if any(kw in query_lower for kw in keywords):
                return domain
        return "general"

    def _estimate_complexity(self, query: str) -> str:
        word_count = len(query.split())
        if word_count < 20:
            return "simple"
        elif word_count < 50:
            return "moderate"
        return "complex"

    def _requires_consensus(self, query: str) -> bool:
        keywords = ["approve", "decide", "recommend", "should we", "critical", "major"]
        return any(kw in query.lower() for kw in keywords)

    async def _execute_agents(
        self,
        agents: List[Agent],
        task: Task,
        context: Dict,
    ) -> Dict[str, Any]:
        """Execute selected agents for the task"""
        results = {}

        if len(agents) == 1:
            result = await self.agent_manager.execute_agent(agents[0], task, context)
            results[agents[0].name] = result
        else:
            tasks = [
                self.agent_manager.execute_agent(agent, task, context)
                for agent in agents
            ]
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            for agent, result in zip(agents, agent_results):
                if isinstance(result, Exception):
                    results[agent.name] = {"error": str(result)}
                else:
                    results[agent.name] = result

        return results

    async def _consolidate_results(
        self,
        results: Dict[str, Any],
        intent: Dict,
        context: Dict,
    ) -> Dict[str, Any]:
        """Consolidate results from multiple agents into a unified response"""
        successful = {k: v for k, v in results.items() if "error" not in v}
        failed = {k: v for k, v in results.items() if "error" in v}

        if intent.get("requires_consensus") and len(successful) > 1:
            decision = await self.decision_manager.make_decision(
                context={"results": successful, "intent": intent},
                options=list(successful.values()),
            )
            return {
                "type": "consensus",
                "decision": decision,
                "individual_results": results,
                "failed_agents": list(failed.keys()),
            }

        return {
            "type": "single" if len(successful) == 1 else "combined",
            "results": successful,
            "failed_agents": list(failed.keys()),
            "summary": self._generate_summary(successful),
        }

    def _generate_summary(self, results: Dict[str, Any]) -> str:
        if not results:
            return "No results available"
        summaries = []
        for agent, result in results.items():
            if isinstance(result, dict) and "summary" in result:
                summaries.append(f"{agent}: {result['summary']}")
            elif isinstance(result, dict) and "output" in result:
                summaries.append(f"{agent}: {str(result['output'])[:100]}")
        return "; ".join(summaries) if summaries else "Results processed"

    async def execute_workflow(
        self,
        workflow: Workflow,
        variables: Optional[Dict] = None,
        security_context: Optional[Dict] = None,
    ) -> WorkflowExecution:
        """Execute a workflow"""
        return await self.workflow_engine.execute(workflow, variables, security_context)

    async def register_agent(self, agent: Agent) -> None:
        """Register a new agent"""
        await self.agent_manager.register(agent)
        self._active_agents.add(agent.id)

    async def unregister_agent(self, agent_id: UUID) -> None:
        """Unregister an agent"""
        await self.agent_manager.unregister(agent_id)
        self._active_agents.discard(agent_id)

    def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        return self.agent_manager.get_agent(agent_id)

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[Agent]:
        return self.agent_manager.list_agents(status)

    def get_task(self, task_id: UUID) -> Optional[Task]:
        return self.task_manager.get_task(task_id)

    def get_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def get_workflow_execution(self, execution_id: UUID) -> Optional[WorkflowExecution]:
        return self._workflow_executions.get(execution_id)

    async def publish_event(self, event: Event) -> None:
        await self.event_bus.publish(event)

    async def subscribe(self, event_type: EventType, handler) -> None:
        await self.event_bus.subscribe(event_type, handler)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "orchestrator_id": str(self.id),
            "running": self._running,
            "active_agents": len(self._active_agents),
            "pending_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.PENDING]),
            "running_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]),
            "active_workflows": len([w for w in self._workflow_executions.values() if w.status == WorkflowStatus.RUNNING]),
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
        }