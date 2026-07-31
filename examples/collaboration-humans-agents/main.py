"""
Collaboration & Team Workspace Engine (Volume 26) — humans + AI agents example.

Runs the corporate scenario from the Volume 26 spec:

    Workspace  : NEXUS ERP PROJECT
    Project    : Sistema Supermercado ERP  (12 humans + 8 AI agents, 74%)
    Request    : "Criar aplicativo de vendas"
    Flow       : Planner -> Task Manager -> Coder -> Human Developer revises
                 -> Security -> Testing -> Deploy
    Approval   : Developer -> Tech Lead -> Security -> Diretor (flow "director")

Run:
    cd SuperDev
    python examples/collaboration-humans-agents/main.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Ensure the SuperDev repo root is importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from collaboration import (EntityKind, MemberRole, ProjectStatus,  # noqa: E402
                           ReviewKind, TeamKind)
from collaboration.collaboration_factory import build_engine  # noqa: E402
from collaboration.tasks.task_status import (  # noqa: E402
    TaskStatus as _TaskStatus,
)
from collaboration.workspace.workspace_engine import (  # noqa: E402
    WorkspaceEngine,
)
from collaboration.teams.team_engine import TeamEngine  # noqa: E402
from collaboration.members.member_engine import MemberEngine  # noqa: E402
from collaboration.projects.project_engine import ProjectEngine  # noqa: E402
from collaboration.tasks.task_engine import TaskEngine  # noqa: E402
from collaboration.comments.comment_engine import CommentEngine  # noqa: E402
from collaboration.reviews.review_engine import ReviewEngine  # noqa: E402
from collaboration.approvals.approval_engine import ApprovalEngine  # noqa: E402
from collaboration.communication.communication_engine import (  # noqa: E402
    CommunicationEngine,
)
from collaboration.knowledge.knowledge_engine import KnowledgeEngine  # noqa: E402


def build_full_engine():
    """Assembles the CollaborationEngine with all ten subsystems attached."""
    engine = build_engine()
    engine.attach_subsystem("workspace_engine", WorkspaceEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        context=engine.context, security=engine.security,
        registry=engine.registry))
    engine.attach_subsystem("team_engine", TeamEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        context=engine.context, security=engine.security,
        registry=engine.registry))
    engine.attach_subsystem("member_engine", MemberEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("project_engine", ProjectEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("task_engine", TaskEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("comment_engine", CommentEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("review_engine", ReviewEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("approval_engine", ApprovalEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("communication_engine", CommunicationEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    engine.attach_subsystem("knowledge_engine", KnowledgeEngine(
        events=engine.events, metrics=engine.metrics, config=engine.config,
        security=engine.security, registry=engine.registry))
    return engine


def run_demo() -> dict[str, Any]:
    engine = build_full_engine()
    engine.start()

    # -- 1. Workspace -------------------------------------------------------
    workspace = engine.workspace_engine.create(
        "NEXUS ERP PROJECT", "owner-nexus",
        description="Projeto ERP para a rede de supermercados Nexus")
    ws_id = workspace.workspace_id

    # -- 2. Teams -----------------------------------------------------------
    dev_team = engine.team_engine.create(
        ws_id, "Desenvolvimento", kind=TeamKind.DEVELOPMENT)
    qa_team = engine.team_engine.create(
        ws_id, "Qualidade", kind=TeamKind.QUALITY)
    ai_team = engine.team_engine.create(
        ws_id, "Agentes IA", kind=TeamKind.AGENTS)

    # -- 3. 12 human members ------------------------------------------------
    diretor = engine.member_engine.add(
        ws_id, "Carlos Diretor", role=MemberRole.OWNER,
        email="carlos@nexus.com.br", skills=["gestao"])
    tech_lead = engine.member_engine.add(
        ws_id, "Ana Tech Lead", role=MemberRole.ADMIN,
        email="ana@nexus.com.br", skills=["arquitetura", "python"],
        team_ids=[dev_team.team_id])
    dev_a = engine.member_engine.add(
        ws_id, "Bruno Backend", role=MemberRole.DEVELOPER,
        email="bruno@nexus.com.br", skills=["python", "api"],
        team_ids=[dev_team.team_id])
    dev_b = engine.member_engine.add(
        ws_id, "Carla Frontend", role=MemberRole.DEVELOPER,
        email="carla@nexus.com.br", skills=["react"],
        team_ids=[dev_team.team_id])
    dev_c = engine.member_engine.add(
        ws_id, "Diego Mobile", role=MemberRole.DEVELOPER,
        email="diego@nexus.com.br", skills=["kotlin"],
        team_ids=[dev_team.team_id])
    db_a = engine.member_engine.add(
        ws_id, "Elena DBA", role=MemberRole.DEVELOPER,
        email="elena@nexus.com.br", skills=["sql", "postgres"],
        team_ids=[dev_team.team_id])
    reviewer_a = engine.member_engine.add(
        ws_id, "Felipe Reviewer", role=MemberRole.REVIEWER,
        email="felipe@nexus.com.br", skills=["code-review"],
        team_ids=[qa_team.team_id])
    security_h = engine.member_engine.add(
        ws_id, "Gisele Security", role=MemberRole.SECURITY,
        email="gisele@nexus.com.br", skills=["pentest"],
        team_ids=[qa_team.team_id])
    tester_a = engine.member_engine.add(
        ws_id, "Hugo Tester", role=MemberRole.REVIEWER,
        email="hugo@nexus.com.br", skills=["qa"],
        team_ids=[qa_team.team_id])
    analyst_a = engine.member_engine.add(
        ws_id, "Iara Analista", role=MemberRole.ANALYST,
        email="iara@nexus.com.br", skills=["negocios"])
    viewer_a = engine.member_engine.add(
        ws_id, "Jorge Stakeholder", role=MemberRole.VIEWER,
        email="jorge@nexus.com.br")
    viewer_b = engine.member_engine.add(
        ws_id, "Kelly Stakeholder", role=MemberRole.VIEWER,
        email="kelly@nexus.com.br")

    # -- 4. 8 AI agents -----------------------------------------------------
    agents = {}
    for name, role, skills in [
        ("Planner IA", MemberRole.ANALYST, ["planejamento"]),
        ("Task Manager IA", MemberRole.DEVELOPER, ["gestao-tarefas"]),
        ("Coder IA", MemberRole.DEVELOPER, ["python", "codegen"]),
        ("Frontend IA", MemberRole.DEVELOPER, ["react", "codegen"]),
        ("Tester IA", MemberRole.REVIEWER, ["qa", "testes"]),
        ("Security IA", MemberRole.SECURITY, ["seguranca"]),
        ("Docs IA", MemberRole.DEVELOPER, ["documentacao"]),
        ("DevOps IA", MemberRole.DEVELOPER, ["deploy", "ci-cd"]),
    ]:
        agents[name] = engine.member_engine.add_agent(
            ws_id, name, role=role, skills=skills)
        agents[name].team_ids.append(ai_team.team_id)

    # -- 5. Project "Sistema Supermercado ERP" ------------------------------
    project = engine.project_engine.create(
        ws_id, "Sistema Supermercado ERP",
        owner_id=tech_lead.member_id,
        description="ERP completo: Vendas, Estoque, Financeiro, RH e Relatórios",
        status=ProjectStatus.ACTIVE)
    prj_id = project.project_id
    for module in ["Vendas", "Estoque", "Financeiro", "RH", "Relatórios"]:
        engine.project_engine.add_module(prj_id, module)
    engine.project_engine.update_progress(prj_id, 74.0)

    # -- 6. Channels --------------------------------------------------------
    geral = engine.communication_engine.create_channel(
        ws_id, "geral", topic="Comunicação geral do projeto")
    vendas_app = engine.communication_engine.create_channel(
        ws_id, "vendas-app", topic="Solicitação: criar aplicativo de vendas")
    ia_agents = engine.communication_engine.create_channel(
        ws_id, "ia-agents", topic="Tráfego dos agentes de IA")

    # -- 7. Request "Criar aplicativo de vendas" ----------------------------
    # Planner IA breaks the request into the task flow.
    engine.communication_engine.send(
        vendas_app.channel_id, agents["Planner IA"].member_id,
        "Plano: task de implementação do módulo Vendas com review humano, "
        "security scan e testes antes do deploy.",
        mentions=[tech_lead.member_id])
    task = engine.task_engine.create(
        prj_id, ws_id, "Criar aplicativo de vendas",
        description="CRUD de vendas + integração com estoque",
        assignee_id=agents["Coder IA"].member_id)
    task_id = task.task_id

    # Coder IA implements -> Human Developer reviews -> Security -> Testing.
    engine.task_engine.update_status(task_id, _TaskStatus.IN_PROGRESS)
    code_review = engine.review_engine.create(
        ReviewKind.CODE, task_id, dev_a.member_id)
    engine.review_engine.decide(
        code_review.review_id, code_review.status, score=92.0,
        findings=[{"severity": "minor", "message": "extrair helper"}])
    engine.task_engine.update_status(task_id, _TaskStatus.IN_REVIEW)

    security_review = engine.review_engine.create(
        ReviewKind.SECURITY, task_id, security_h.member_id)
    engine.review_engine.decide_auto(
        security_review.review_id,
        findings=[{"severity": "major", "message": "validar input na API"}])
    testing_review = engine.review_engine.create(
        ReviewKind.PROCESS, task_id, tester_a.member_id)
    engine.review_engine.decide_auto(testing_review.review_id, findings=[])
    engine.task_engine.update_status(task_id, _TaskStatus.DONE)

    engine.project_engine.update_progress(prj_id, 80.0)

    # -- 8. Director approval chain ----------------------------------------
    approval = engine.approval_engine.start(
        EntityKind.TASK, task_id,
        requested_by=agents["Task Manager IA"].member_id,
        flow="director")
    approval_id = approval.approval_id
    for decider, reason in [
        (dev_a.member_id, "Implementação aprovada pelo desenvolvedor"),
        (tech_lead.member_id, "Tech Lead validou arquitetura"),
        (security_h.member_id, "Security liberou após correções"),
        (diretor.member_id, "Diretor aprovou para deploy"),
    ]:
        engine.approval_engine.decide(approval_id, True, decider, reason)

    # -- 9. Communication between humans and agents ------------------------
    engine.communication_engine.send(
        vendas_app.channel_id, agents["DevOps IA"].member_id,
        "Deploy realizado no ambiente de homologação.",
        mentions=[dev_a.member_id, tech_lead.member_id])
    engine.communication_engine.send(
        geral.channel_id, diretor.member_id,
        "Excelente colaboração humanos + IA nesta entrega!")
    engine.communication_engine.send_dm(
        tech_lead.member_id, dev_a.member_id,
        "Bruno, revise a task de vendas antes do deploy.")

    # -- 10. Knowledge base -------------------------------------------------
    page = engine.knowledge_engine.create(
        ws_id, "Manual do Módulo de Vendas",
        "Fluxo de vendas, integração com estoque e regras de negócio.",
        agents["Docs IA"].member_id, tags=["vendas", "manual"])
    engine.knowledge_engine.edit(
        page.document_id,
        "Fluxo de vendas, integração com estoque, regras e segurança.",
        dev_a.member_id, tags=["vendas", "manual", "seguranca"])

    engine.stop()
    return {
        "workspace": workspace.name,
        "project": project.name,
        "project_status": project.status.value,
        "progress": project.progress,
        "members_humans": 12,
        "members_agents": len(agents),
        "teams": engine.team_engine.manager.count(),
        "channels": engine.communication_engine.stats()["channels"],
        "task": task.title,
        "task_status": engine.task_engine.get(task_id).status.value,
        "code_review_score": engine.review_engine.get(
            code_review.review_id).score,
        "security_review": engine.review_engine.get(
            security_review.review_id).status.value,
        "testing_review": engine.review_engine.get(
            testing_review.review_id).status.value,
        "approval": engine.approval_engine.get(approval_id).status.value,
        "approval_steps": len(engine.approval_engine.steps("director")),
        "knowledge_version": engine.knowledge_engine.get(
            page.document_id).version,
        "messages": engine.communication_engine.stats()["messages"],
        "comments": engine.comment_engine.manager.count(),
        "metrics": engine.metrics.snapshot(),
    }


def main() -> dict[str, Any]:
    return run_demo()


if __name__ == "__main__":
    result = main()
    print("\n=== Collaboration & Team Workspace Engine — Example Output ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
