from __future__ import annotations

import os
from typing import Any

import httpx


class GitHubChecksClient:
    def __init__(self):
        self._token = os.getenv("GITHUB_TOKEN", "")
        self._headers = (
            {
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github.v3+json",
            }
            if self._token
            else {}
        )

    async def create_check_run(self, repo: str, sha: str, name: str = "SuperDev Code Review") -> dict[str, Any]:
        if not self._token:
            return {"id": 0, "status": "skipped"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/repos/{repo}/check-runs",
                headers=self._headers,
                json={
                    "name": name,
                    "head_sha": sha,
                    "status": "in_progress",
                    "started_at": __import__("datetime").datetime.utcnow().isoformat(),
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def update_check_run(
        self, repo: str, check_run_id: int, conclusion: str, output: dict[str, Any]
    ) -> dict[str, Any]:
        if not self._token:
            return {"status": "skipped"}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(
                f"https://api.github.com/repos/{repo}/check-runs/{check_run_id}",
                headers=self._headers,
                json={
                    "status": "completed",
                    "conclusion": conclusion,
                    "completed_at": __import__("datetime").datetime.utcnow().isoformat(),
                    "output": output,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_pr_files(self, repo: str, pr_number: int) -> list[dict[str, Any]]:
        if not self._token:
            return self._mock_files()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        if not self._token:
            return ""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
                headers={**self._headers, "Accept": "application/vnd.github.v3.diff"},
            )
            resp.raise_for_status()
            return resp.text

    async def create_pr_review(
        self, repo: str, pr_number: int, body: str, event: str = "COMMENT", comments: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        if not self._token:
            return {"id": 0}
        async with httpx.AsyncClient() as client:
            payload: dict[str, Any] = {"body": body, "event": event}
            if comments:
                payload["comments"] = comments
            resp = await client.post(
                f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    def _mock_files(self) -> list[dict[str, Any]]:
        return [
            {
                "filename": "src/main.py",
                "status": "modified",
                "additions": 50,
                "deletions": 10,
                "patch": "@@ -1,5 +1,10 @@\n+import os\n+def new_func():\n+    pass",
            },
            {
                "filename": "src/agent.py",
                "status": "added",
                "additions": 120,
                "deletions": 0,
                "patch": "@@ -0,0 +1,120 @@\n+class Agent:\n+    def run(self):\n+        pass",
            },
        ]

    def is_configured(self) -> bool:
        return bool(self._token)
