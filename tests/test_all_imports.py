"""Teste completo de todos os módulos."""

import asyncio
import sys
sys.path.insert(0, ".")

print("=" * 60)
print("TESTE DE IMPORTAÇÃO - TODOS OS MÓDULOS")
print("=" * 60)

# 1. ConditionNode
print("\n[1] ConditionNode (Parser Seguro):")
from workflow_engine.nodes.condition_node import safe_condition_eval, ConditionNode
result = safe_condition_eval("x > 5", {"x": 10})
print(f"  safe_condition_eval('x > 5', {{x: 10}}) = {result}")
assert result is True
result2 = safe_condition_eval("a and b", {"a": True, "b": False})
print(f"  safe_condition_eval('a and b', {{a: True, b: False}}) = {result2}")
assert result2 is False
print("  ✅ PASSOU - 2/2")

# 2. Planner
print("\n[2] Planner (Decomposição via LLM):")
from agents.planner.planner import Planner
planner = Planner()
steps = asyncio.run(planner.plan("Criar um projeto completo"))
print(f"  plan() gerou {len(steps)} steps")
assert len(steps) > 0
print(f"  Step 1: {steps[0].description[:50]}...")
print("  ✅ PASSOU")

# 3. Sandbox
print("\n[3] Sandbox (Isolamento):")
from runtime_engine.sandbox.sandbox import DefaultSandbox, SandboxPolicy, create_sandbox
policy = SandboxPolicy()
print(f"  SandboxPolicy(max_memory_mb={policy.max_memory_mb})")
sandbox = create_sandbox(use_docker=False)
print(f"  create_sandbox() = {type(sandbox).__name__}")
assert sandbox is not None
print("  ✅ PASSOU")

# 4. JobManager
print("\n[4] JobManager (Background Jobs):")
from backend.jobs.job_manager import JobManager, Job, JobStatus
jm = JobManager(max_workers=2)
print(f"  JobManager(max_workers=2)")
job = Job(job_type="test", payload={"key": "value"})
print(f"  Job(type={job.type}, status={job.status.value})")
assert job.status == JobStatus.PENDING
print("  ✅ PASSOU")

# 5. HealthChecker
print("\n[5] HealthChecker (Monitoramento):")
from backend.health_monitor import health_monitor, check_system, check_disk_space, check_memory
result = check_system()
print(f"  check_system() = {result.status}")
print(f"  CPU: {result.details.get('cpu_percent', 0):.1f}%")
print(f"  RAM: {result.details.get('memory_percent', 0):.1f}%")
print(f"  Disco: {result.details.get('disk_percent', 0):.1f}%")
assert result.status in ["healthy", "degraded", "unhealthy"]
print("  ✅ PASSOU")

# 6. WebSocket Events
print("\n[6] WebSocket Events (Tempo Real):")
from backend.ws_events import ws_manager, WsEvent
event = WsEvent("test", {"msg": "hello"})
print(f"  WsEvent(type={event.type}, room={event.room})")
assert event.type == "test"
print(f"  to_json() = {event.to_json()[:80]}...")
print("  ✅ PASSOU")

# 7. Seed Data
print("\n[7] Seed Data (Dados Realistas):")
from backend.database.seeds.seed_data import get_all_seed_data, USERS, PROJECTS, AGENTS, WORKFLOWS
data = get_all_seed_data()
print(f"  Total tabelas: {len(data)}")
for table, rows in data.items():
    print(f"    {table}: {len(rows)} registros")
assert len(data) > 0
assert len(USERS) == 3
assert len(PROJECTS) == 3
assert len(AGENTS) == 4
print("  ✅ PASSOU")

# 8. Alembic Migration
print("\n[8] Alembic Migration:")
import os
migration_exists = os.path.exists("backend/database/migrations/env.py")
version_exists = os.path.exists("backend/database/migrations/versions/0001_initial.py")
print(f"  env.py existe: {migration_exists}")
print(f"  0001_initial.py existe: {version_exists}")
assert migration_exists
assert version_exists
print("  ✅ PASSOU")

# Resumo
print("\n" + "=" * 60)
print("RESUMO DOS TESTES")
print("=" * 60)
print("[✅] ConditionNode (Parser Seguro)")
print("[✅] Planner (Decomposição via LLM)")
print("[✅] Sandbox (Isolamento)")
print("[✅] JobManager (Background Jobs)")
print("[✅] HealthChecker (Monitoramento)")
print("[✅] WebSocket Events (Tempo Real)")
print("[✅] Seed Data (Dados Realistas)")
print("[✅] Alembic Migration")
print("=" * 60)
print("TODOS OS 8 MÓDULOS FUNCIONANDO!")
print("=" * 60)
