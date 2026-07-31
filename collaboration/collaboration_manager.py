"""Manager for the Collaboration & Team Workspace Engine.

Coordinates workspaces, teams, members, projects, tasks, comments,
reviews, approvals, communication and knowledge. Subsystem engines are
attached lazily by the engine facade.
"""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_events import CollaborationEventType
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_models import (
    ApprovalRecord, ApprovalStatus, ChannelRecord, CommentRecord, EntityKind,
    KnowledgeRecord, MemberKind, MemberRecord, MemberRole, MemberStatus,
    MessageKind, MessageRecord, ProjectRecord, ProjectStatus, ReviewKind,
    ReviewRecord, ReviewStatus, TaskPriority, TaskRecord, TaskStatus,
    TeamKind, TeamRecord, WorkspaceRecord,
)
from collaboration.collaboration_protocols import new_id


class CollaborationManager:
    """High-level operations over the engine's registries."""

    def __init__(self, registry: Any, events: Any, metrics: Any,
                 config: Any, context: Any, security: Any,
                 engine: Any = None) -> None:
        self._log = get_logger()
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.security = security
        self.engine: Any = engine

    # -- workspaces ---------------------------------------------------------
    def create_workspace(self, name: str, owner_id: str,
                         description: str = "",
                         **settings: Any) -> WorkspaceRecord:
        workspace = WorkspaceRecord(workspace_id=new_id("ws"), name=name,
                                    owner_id=owner_id,
                                    description=description,
                                    settings=settings,
                                    created_at=time.time())
        self.registry.register_workspace(workspace.workspace_id, workspace)
        self.metrics.increment("collab.workspaces")
        self.events.publish(CollaborationEventType.WORKSPACE_CREATED,
                            {"workspace_id": workspace.workspace_id,
                             "name": name})
        return workspace

    def list_workspaces(self) -> list[str]:
        return self.registry.list_workspaces()

    def get_workspace(self, workspace_id: str) -> WorkspaceRecord | None:
        return self.registry.get_workspace(workspace_id)

    def remove_workspace(self, workspace_id: str) -> bool:
        return self.registry.remove_workspace(workspace_id)

    # -- teams --------------------------------------------------------------
    def create_team(self, workspace_id: str, name: str,
                    kind: TeamKind = TeamKind.DEVELOPMENT,
                    lead_id: str | None = None,
                    description: str = "") -> TeamRecord:
        team = TeamRecord(team_id=new_id("team"), workspace_id=workspace_id,
                          name=name, kind=kind, lead_id=lead_id,
                          description=description)
        self.registry.register_team(team.team_id, team)
        self.metrics.increment("collab.teams")
        self.events.publish(CollaborationEventType.TEAM_CREATED,
                            {"team_id": team.team_id, "name": name})
        return team

    def list_teams(self) -> list[str]:
        return self.registry.list_teams()

    def get_team(self, team_id: str) -> TeamRecord | None:
        return self.registry.get_team(team_id)

    def remove_team(self, team_id: str) -> bool:
        return self.registry.remove_team(team_id)

    # -- members ------------------------------------------------------------
    def add_member(self, workspace_id: str, name: str,
                   kind: MemberKind = MemberKind.HUMAN,
                   role: MemberRole = MemberRole.DEVELOPER,
                   email: str = "",
                   skills: list[str] | None = None,
                   team_ids: list[str] | None = None) -> MemberRecord:
        member = MemberRecord(member_id=new_id("mem"),
                              workspace_id=workspace_id, name=name, kind=kind,
                              role=role, email=email,
                              status=MemberStatus.ACTIVE,
                              skills=list(skills or []),
                              team_ids=list(team_ids or []))
        self.registry.register_member(member.member_id, member)
        self.metrics.increment("collab.members")
        self.events.publish(CollaborationEventType.MEMBER_JOINED,
                            {"member_id": member.member_id, "name": name,
                             "kind": kind.value})
        return member

    def add_agent(self, workspace_id: str, name: str,
                  role: MemberRole = MemberRole.DEVELOPER,
                  skills: list[str] | None = None,
                  team_ids: list[str] | None = None) -> MemberRecord:
        return self.add_member(workspace_id, name, kind=MemberKind.AGENT,
                               role=role, skills=skills, team_ids=team_ids)

    def list_members(self) -> list[str]:
        return self.registry.list_members()

    def get_member(self, member_id: str) -> MemberRecord | None:
        return self.registry.get_member(member_id)

    def remove_member(self, member_id: str) -> bool:
        member = self.registry.get_member(member_id)
        if member is not None:
            self.events.publish(CollaborationEventType.MEMBER_LEFT,
                                {"member_id": member_id,
                                 "name": member.name})
        return self.registry.remove_member(member_id)

    # -- projects -----------------------------------------------------------
    def create_project(self, workspace_id: str, name: str,
                       owner_id: str = "",
                       description: str = "") -> ProjectRecord:
        project = ProjectRecord(project_id=new_id("proj"),
                                workspace_id=workspace_id, name=name,
                                status=ProjectStatus.PLANNING,
                                description=description, owner_id=owner_id)
        self.registry.register_project(project.project_id, project)
        self.metrics.increment("collab.projects")
        self.events.publish(CollaborationEventType.PROJECT_CREATED,
                            {"project_id": project.project_id, "name": name})
        return project

    def list_projects(self) -> list[str]:
        return self.registry.list_projects()

    def get_project(self, project_id: str) -> ProjectRecord | None:
        return self.registry.get_project(project_id)

    def update_project_progress(self, project_id: str,
                                progress: float) -> ProjectRecord | None:
        project = self.registry.get_project(project_id)
        if project is None:
            return None
        project.progress = max(0.0, min(100.0, float(progress)))
        self.metrics.gauge(f"collab.progress.{project_id}", project.progress)
        self.events.publish(CollaborationEventType.PROJECT_UPDATED,
                            {"project_id": project_id,
                             "progress": project.progress})
        return project

    def remove_project(self, project_id: str) -> bool:
        return self.registry.remove_project(project_id)

    # -- tasks --------------------------------------------------------------
    def create_task(self, project_id: str, workspace_id: str, title: str,
                    created_by: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    assignee_id: str | None = None,
                    description: str = "",
                    parent_id: str | None = None) -> TaskRecord:
        task = TaskRecord(task_id=new_id("task"), project_id=project_id,
                          workspace_id=workspace_id, title=title,
                          priority=priority, assignee_id=assignee_id,
                          created_by=created_by, description=description,
                          parent_id=parent_id)
        self.registry.register_task(task.task_id, task)
        self.metrics.increment("collab.tasks")
        self.events.publish(CollaborationEventType.TASK_CREATED,
                            {"task_id": task.task_id, "title": title,
                             "project_id": project_id})
        if assignee_id is not None:
            self.events.publish(CollaborationEventType.TASK_ASSIGNED,
                                {"task_id": task.task_id,
                                 "assignee_id": assignee_id})
        return task

    def assign_task(self, task_id: str, assignee_id: str) -> TaskRecord | None:
        task = self.registry.get_task(task_id)
        if task is None:
            return None
        task.assignee_id = assignee_id
        self.events.publish(CollaborationEventType.TASK_ASSIGNED,
                            {"task_id": task_id, "assignee_id": assignee_id})
        return task

    def update_task_status(self, task_id: str,
                           status: TaskStatus) -> TaskRecord | None:
        task = self.registry.get_task(task_id)
        if task is None:
            return None
        task.status = status
        if status == TaskStatus.DONE:
            task.progress = 100.0
            self.events.publish(CollaborationEventType.TASK_COMPLETED,
                                {"task_id": task_id})
        else:
            self.events.publish(CollaborationEventType.TASK_UPDATED,
                                {"task_id": task_id, "status": status.value})
        return task

    def list_tasks(self) -> list[str]:
        return self.registry.list_tasks()

    def get_task(self, task_id: str) -> TaskRecord | None:
        return self.registry.get_task(task_id)

    def remove_task(self, task_id: str) -> bool:
        return self.registry.remove_task(task_id)

    # -- comments -----------------------------------------------------------
    def add_comment(self, target_kind: EntityKind, target_id: str,
                    author_id: str, body: str) -> CommentRecord:
        comment = CommentRecord(comment_id=new_id("cmt"),
                                target_kind=target_kind, target_id=target_id,
                                author_id=author_id, body=body,
                                mentions=[],
                                created_at=time.time())
        self.registry.add_comment(comment)
        self.metrics.increment("collab.comments")
        self.events.publish(CollaborationEventType.COMMENT_ADDED,
                            {"comment_id": comment.comment_id,
                             "target_kind": target_kind.value,
                             "target_id": target_id, "author_id": author_id})
        return comment

    def comments_for(self, target_id: str) -> list[CommentRecord]:
        return self.registry.comments_for(target_id)

    # -- reviews ------------------------------------------------------------
    def create_review(self, target_kind: ReviewKind, target_id: str,
                      author_id: str) -> ReviewRecord:
        review = ReviewRecord(review_id=new_id("rev"), target_kind=target_kind,
                              target_id=target_id, author_id=author_id,
                              created_at=time.time())
        self.registry.register_review(review.review_id, review)
        self.metrics.increment("collab.reviews")
        self.events.publish(CollaborationEventType.REVIEW_CREATED,
                            {"review_id": review.review_id,
                             "target_kind": target_kind.value,
                             "target_id": target_id})
        return review

    def decide_review(self, review_id: str, status: ReviewStatus,
                      score: float, findings: list[dict[str, Any]],
                      ) -> ReviewRecord | None:
        review = self.registry.get_review(review_id)
        if review is None:
            return None
        review.status = status
        review.score = max(0.0, min(100.0, float(score)))
        review.findings = list(findings)
        self.events.publish(CollaborationEventType.REVIEW_DECIDED,
                            {"review_id": review_id, "status": status.value,
                             "score": review.score,
                             "findings": len(findings)})
        return review

    def get_review(self, review_id: str) -> ReviewRecord | None:
        return self.registry.get_review(review_id)

    # -- approvals ----------------------------------------------------------
    def start_approval(self, target_kind: EntityKind, target_id: str,
                       requested_by: str, flow: str = "manager") -> ApprovalRecord:
        approval = ApprovalRecord(approval_id=new_id("appr"),
                                  target_kind=target_kind,
                                  target_id=target_id, flow=flow,
                                  requested_by=requested_by)
        self.registry.register_approval(approval.approval_id, approval)
        self.metrics.increment("collab.approvals")
        self.events.publish(CollaborationEventType.APPROVAL_STARTED,
                            {"approval_id": approval.approval_id,
                             "target_kind": target_kind.value,
                             "target_id": target_id, "flow": flow})
        return approval

    def decide_approval(self, approval_id: str, approved: bool,
                        decider: str, reason: str = "") -> ApprovalRecord | None:
        approval = self.registry.get_approval(approval_id)
        if approval is None:
            return None
        approval.status = (ApprovalStatus.APPROVED if approved
                           else ApprovalStatus.REJECTED)
        approval.decided_by = decider
        approval.decided_at = time.time()
        approval.reason = reason
        self.events.publish(CollaborationEventType.APPROVAL_DECIDED,
                            {"approval_id": approval_id,
                             "status": approval.status.value,
                             "decided_by": decider})
        return approval

    def get_approval(self, approval_id: str) -> ApprovalRecord | None:
        return self.registry.get_approval(approval_id)

    # -- communication ------------------------------------------------------
    def create_channel(self, workspace_id: str, name: str,
                       topic: str = "") -> ChannelRecord:
        channel = ChannelRecord(channel_id=new_id("ch"),
                                workspace_id=workspace_id, name=name,
                                topic=topic)
        self.registry.register_channel(channel.channel_id, channel)
        self.metrics.increment("collab.channels")
        return channel

    def send_message(self, channel_id: str, author_id: str, body: str,
                     kind: MessageKind = MessageKind.CHAT) -> MessageRecord:
        message = MessageRecord(message_id=new_id("msg"),
                                channel_id=channel_id, author_id=author_id,
                                body=body, kind=kind, created_at=time.time())
        self.registry.add_message(message)
        self.metrics.increment("collab.messages")
        self.events.publish(CollaborationEventType.MESSAGE_SENT,
                            {"message_id": message.message_id,
                             "channel_id": channel_id,
                             "author_id": author_id})
        return message

    def messages_for(self, channel_id: str) -> list[MessageRecord]:
        return self.registry.messages_for(channel_id)

    # -- knowledge ----------------------------------------------------------
    def add_document(self, workspace_id: str, title: str, body: str,
                     author_id: str = "", tags: list[str] | None = None
                     ) -> KnowledgeRecord:
        document = KnowledgeRecord(document_id=new_id("doc"),
                                   workspace_id=workspace_id, title=title,
                                   body=body, author_id=author_id,
                                   tags=list(tags or []),
                                   updated_at=time.time())
        self.registry.register_document(document.document_id, document)
        self.metrics.increment("collab.documents")
        self.events.publish(CollaborationEventType.DOCUMENT_CREATED,
                            {"document_id": document.document_id,
                             "title": title})
        return document

    def get_document(self, document_id: str) -> KnowledgeRecord | None:
        return self.registry.get_document(document_id)

    def list_documents(self) -> list[str]:
        return self.registry.list_documents()

    def search_documents(self, query: str) -> list[KnowledgeRecord]:
        q = query.lower()
        results: list[KnowledgeRecord] = []
        for document_id in self.list_documents():
            document = self.get_document(document_id)
            if document is None:
                continue
            haystack = f"{document.title} {document.body} " \
                       f"{' '.join(document.tags)}".lower()
            if q in haystack:
                results.append(document)
        return results

    # -- stats --------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return self.registry.stats()
