"""Registry for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from typing import Any


class CollaborationRegistry:
    """Central registry for workspaces, teams, members, projects, tasks,
    comments, reviews, approvals, channels, messages and documents."""

    def __init__(self) -> None:
        self._workspaces: dict[str, Any] = {}
        self._teams: dict[str, Any] = {}
        self._members: dict[str, Any] = {}
        self._projects: dict[str, Any] = {}
        self._tasks: dict[str, Any] = {}
        self._comments: dict[str, list[Any]] = {}
        self._reviews: dict[str, Any] = {}
        self._approvals: dict[str, Any] = {}
        self._channels: dict[str, Any] = {}
        self._messages: dict[str, list[Any]] = {}
        self._documents: dict[str, Any] = {}

    # -- workspaces ---------------------------------------------------------
    def register_workspace(self, workspace_id: str, workspace: Any) -> None:
        self._workspaces[workspace_id] = workspace

    def get_workspace(self, workspace_id: str) -> Any | None:
        return self._workspaces.get(workspace_id)

    def list_workspaces(self) -> list[str]:
        return list(self._workspaces)

    def remove_workspace(self, workspace_id: str) -> bool:
        return self._workspaces.pop(workspace_id, None) is not None

    # -- teams --------------------------------------------------------------
    def register_team(self, team_id: str, team: Any) -> None:
        self._teams[team_id] = team

    def get_team(self, team_id: str) -> Any | None:
        return self._teams.get(team_id)

    def list_teams(self) -> list[str]:
        return list(self._teams)

    def remove_team(self, team_id: str) -> bool:
        return self._teams.pop(team_id, None) is not None

    # -- members ------------------------------------------------------------
    def register_member(self, member_id: str, member: Any) -> None:
        self._members[member_id] = member

    def get_member(self, member_id: str) -> Any | None:
        return self._members.get(member_id)

    def list_members(self) -> list[str]:
        return list(self._members)

    def remove_member(self, member_id: str) -> bool:
        return self._members.pop(member_id, None) is not None

    # -- projects -----------------------------------------------------------
    def register_project(self, project_id: str, project: Any) -> None:
        self._projects[project_id] = project

    def get_project(self, project_id: str) -> Any | None:
        return self._projects.get(project_id)

    def list_projects(self) -> list[str]:
        return list(self._projects)

    def remove_project(self, project_id: str) -> bool:
        return self._projects.pop(project_id, None) is not None

    # -- tasks --------------------------------------------------------------
    def register_task(self, task_id: str, task: Any) -> None:
        self._tasks[task_id] = task

    def get_task(self, task_id: str) -> Any | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[str]:
        return list(self._tasks)

    def remove_task(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None

    # -- comments -----------------------------------------------------------
    def add_comment(self, comment: Any) -> None:
        self._comments.setdefault(comment.target_id, []).append(comment)

    def comments_for(self, target_id: str) -> list[Any]:
        return list(self._comments.get(target_id, []))

    def remove_comments(self, target_id: str) -> None:
        self._comments.pop(target_id, None)

    # -- reviews ------------------------------------------------------------
    def register_review(self, review_id: str, review: Any) -> None:
        self._reviews[review_id] = review

    def get_review(self, review_id: str) -> Any | None:
        return self._reviews.get(review_id)

    def list_reviews(self) -> list[str]:
        return list(self._reviews)

    def remove_review(self, review_id: str) -> bool:
        return self._reviews.pop(review_id, None) is not None

    # -- approvals ----------------------------------------------------------
    def register_approval(self, approval_id: str, approval: Any) -> None:
        self._approvals[approval_id] = approval

    def get_approval(self, approval_id: str) -> Any | None:
        return self._approvals.get(approval_id)

    def list_approvals(self) -> list[str]:
        return list(self._approvals)

    def remove_approval(self, approval_id: str) -> bool:
        return self._approvals.pop(approval_id, None) is not None

    # -- channels -----------------------------------------------------------
    def register_channel(self, channel_id: str, channel: Any) -> None:
        self._channels[channel_id] = channel

    def get_channel(self, channel_id: str) -> Any | None:
        return self._channels.get(channel_id)

    def list_channels(self) -> list[str]:
        return list(self._channels)

    def remove_channel(self, channel_id: str) -> bool:
        return self._channels.pop(channel_id, None) is not None

    # -- messages -----------------------------------------------------------
    def add_message(self, message: Any) -> None:
        self._messages.setdefault(message.channel_id, []).append(message)

    def messages_for(self, channel_id: str) -> list[Any]:
        return list(self._messages.get(channel_id, []))

    # -- documents ----------------------------------------------------------
    def register_document(self, document_id: str, document: Any) -> None:
        self._documents[document_id] = document

    def get_document(self, document_id: str) -> Any | None:
        return self._documents.get(document_id)

    def list_documents(self) -> list[str]:
        return list(self._documents)

    def remove_document(self, document_id: str) -> bool:
        return self._documents.pop(document_id, None) is not None

    def stats(self) -> dict[str, int]:
        return {"workspaces": len(self._workspaces), "teams": len(self._teams),
                "members": len(self._members), "projects": len(self._projects),
                "tasks": len(self._tasks),
                "comments": sum(len(v) for v in self._comments.values()),
                "reviews": len(self._reviews),
                "approvals": len(self._approvals),
                "channels": len(self._channels),
                "messages": sum(len(v) for v in self._messages.values()),
                "documents": len(self._documents)}
