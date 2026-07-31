from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from .pr_manager import PRManager
from .template import PRTemplateEngine

router = APIRouter(prefix="/github/webhook", tags=["github"])
_pr_manager = PRManager()
_template_engine = PRTemplateEngine()


def _verify_signature(payload: bytes, signature: str | None) -> bool:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    if not secret or not signature:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("")
async def handle_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("x-hub-signature-256")
    event = request.headers.get("x-github-event", "")

    if not _verify_signature(body, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    import json

    payload = json.loads(body)

    if event == "issues" and payload.get("action") in ("opened", "labeled"):
        issue = payload["issue"]
        labels = [l["name"] for l in issue.get("labels", [])]
        if any(lb in labels for lb in ("pr-auto", "superdev", "ai", "auto-pr", "feature")):
            return await _handle_issue(issue, payload.get("repository", {}))
        return {"status": "skipped", "reason": "no matching label"}

    if event == "issue_comment" and payload.get("action") == "created":
        comment = payload["comment"]["body"].strip().lower()
        if comment in ("/superdev", "/generate-pr", "/auto-pr"):
            return await _handle_issue(payload["issue"], payload.get("repository", {}))
        return {"status": "skipped", "reason": "no matching command"}

    return {"status": "ignored", "event": event}


async def _handle_issue(issue: dict[str, Any], repo: dict[str, Any]) -> dict[str, Any]:
    issue_number = issue["number"]
    title = issue["title"]
    body = issue.get("body", "")
    repo_full = repo.get("full_name", "unknown/repo")

    template = _template_engine.generate(title, body)
    result = await _pr_manager.create_pr(repo_full, title, template, issue_number)

    return {
        "status": "pr_created" if result.get("pr_url") else "failed",
        "issue": issue_number,
        "repo": repo_full,
        "pr_url": result.get("pr_url"),
        "branch": result.get("branch"),
    }


@router.get("/config")
async def get_config() -> dict[str, Any]:
    return {
        "triggers": ["issue opened", "label added", "comment /superdev"],
        "auto_labels": ["pr-auto", "superdev", "ai", "auto-pr", "feature"],
        "commands": ["/superdev", "/generate-pr", "/auto-pr"],
    }
