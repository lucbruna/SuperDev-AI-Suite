from __future__ import annotations

import os
import uuid
from typing import Any

import httpx


class PRManager:
    def __init__(self):
        self._github_token = os.getenv("GITHUB_TOKEN", "")
        self._base_url = "https://api.github.com"
        self._headers = (
            {
                "Authorization": f"Bearer {self._github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            if self._github_token
            else {}
        )

    async def create_pr(self, repo: str, title: str, body: str, issue_number: int) -> dict[str, Any]:
        branch_name = f"auto/pr-{issue_number}-{uuid.uuid4().hex[:6]}"
        base_branch = await self._get_default_branch(repo)

        try:
            await self._create_branch(repo, branch_name, base_branch)
            await self._create_commit(repo, branch_name, title, body)
            pr = await self._open_pr(repo, title, body, branch_name, base_branch, issue_number)
            return {"pr_url": pr.get("html_url"), "branch": branch_name, "pr_number": pr.get("number")}
        except Exception as e:
            return {"error": str(e), "branch": branch_name}

    async def _get_default_branch(self, repo: str) -> str:
        if not self._github_token:
            return "main"
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._base_url}/repos/{repo}", headers=self._headers)
            resp.raise_for_status()
            return resp.json().get("default_branch", "main")

    async def _create_branch(self, repo: str, branch: str, base: str) -> None:
        if not self._github_token:
            return
        async with httpx.AsyncClient() as client:
            ref_resp = await client.get(f"{self._base_url}/repos/{repo}/git/ref/heads/{base}", headers=self._headers)
            ref_resp.raise_for_status()
            sha = ref_resp.json()["object"]["sha"]
            await client.post(
                f"{self._base_url}/repos/{repo}/git/refs",
                headers=self._headers,
                json={"ref": f"refs/heads/{branch}", "sha": sha},
            )

    async def _create_commit(self, repo: str, branch: str, title: str, body: str) -> None:
        if not self._github_token:
            return
        async with httpx.AsyncClient() as client:
            readme_resp = await client.get(f"{self._base_url}/repos/{repo}/contents/README.md", headers=self._headers)
            if readme_resp.status_code == 200:
                content = readme_resp.json()
                new_content = f"# Auto-generated from issue\n\n{body}\n\n---\n\n{content.get('content', '')}"
                import base64

                try:
                    decoded = base64.b64decode(content["content"]).decode()
                    new_content = f"# Auto-generated from issue\n\n{body}\n\n---\n\n{decoded}"
                except Exception:
                    pass
                await client.put(
                    f"{self._base_url}/repos/{repo}/contents/README.md",
                    headers=self._headers,
                    json={
                        "message": f"Auto PR: {title}",
                        "content": base64.b64encode(new_content.encode()).decode(),
                        "sha": content["sha"],
                        "branch": branch,
                    },
                )

    async def _open_pr(
        self, repo: str, title: str, body: str, branch: str, base: str, issue_number: int
    ) -> dict[str, Any]:
        if not self._github_token:
            return {"html_url": f"https://github.com/{repo}/pull/new/{branch}", "number": 0}
        async with httpx.AsyncClient() as client:
            pr_body = f"{body}\n\n---\n_Automatically generated from issue #{issue_number}_\nCloses #{issue_number}"
            resp = await client.post(
                f"{self._base_url}/repos/{repo}/pulls",
                headers=self._headers,
                json={"title": title, "body": pr_body, "head": branch, "base": base},
            )
            resp.raise_for_status()
            return resp.json()

    def is_configured(self) -> bool:
        return bool(self._github_token)
