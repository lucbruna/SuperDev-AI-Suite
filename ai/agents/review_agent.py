from __future__ import annotations

from typing import Any

from backend.code_review.review_engine import ReviewEngine
from backend.code_review.check_runner import GitHubChecksClient
from backend.code_review.config import ReviewConfig


class CodeReviewAgent:
    def __init__(self):
        self._engine = ReviewEngine()
        self._checks = GitHubChecksClient()

    async def review_pr(self, repo: str, pr_number: int, sha: str) -> dict[str, Any]:
        files = await self._checks.get_pr_files(repo, pr_number)
        diff = await self._checks.get_pr_diff(repo, pr_number)
        result = await self._engine.review_pr(files, diff)
        check_run = await self._checks.create_check_run(repo, sha)
        if check_run.get("id"):
            output = {
                "title": f"SuperDev Review: {result['conclusion'].upper()} ({result['score']}/10)",
                "summary": result["summary"],
                "text": "\n".join(f"- {c['body'][:100]}" for c in result.get("comments", [])),
            }
            await self._checks.update_check_run(repo, check_run["id"], result["conclusion"], output)
        if result.get("comments"):
            await self._checks.create_pr_review(repo, pr_number, result["summary"], "COMMENT", result["comments"])
        return result

    async def review_diff(self, diff: str, filename: str = "unknown") -> dict[str, Any]:
        files = [{"filename": filename, "patch": diff, "status": "modified", "additions": len(diff.split("\n")), "deletions": 0}]
        return await self._engine.review_pr(files, diff)

    def get_config(self) -> list[dict[str, Any]]:
        return self._engine._config.get_all_rules()