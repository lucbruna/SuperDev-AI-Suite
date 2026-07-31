from __future__ import annotations

from typing import Any

from ..base.base_agent import AgentResult, BaseAgent
from ..tools.http_tool import HTTPTool
from ..tools.search_tool import SearchTool


class ResearchAgent(BaseAgent):
    async def initialize(self) -> None:
        self._search_tool = SearchTool()
        self._http_tool = HTTPTool()
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            search_results = await self._search_tool.execute(
                {
                    "pattern": context.get("search_pattern", task),
                    "path": context.get("path", "."),
                    "type": context.get("search_type", "file"),
                }
            )

            web_results = []
            urls = context.get("urls", [])
            for url in urls:
                result = await self._http_tool.execute(
                    {
                        "url": url,
                        "method": "GET",
                        "timeout": 30,
                    }
                )
                if result.get("success"):
                    web_results.append({"url": url, "content": result.get("body", "")[:2000]})

            summary = self._generate_summary(task, search_results, web_results)

            return AgentResult(
                success=True,
                output=summary,
                metrics={
                    "local_findings": search_results.get("count", 0),
                    "web_sources": len(web_results),
                },
                artifacts={
                    "search_results": search_results.get("results", []),
                    "web_results": web_results,
                },
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def _generate_summary(self, task: str, search: dict, web: list) -> str:
        lines = [
            f"## Research Summary: {task[:60]}",
            "",
            "### Local Search Results",
            f"Found {search.get('count', 0)} matches",
            "",
            f"### Web Sources Consulted: {len(web)}",
        ]
        for w in web:
            lines.append(f"- {w['url']}: {len(w['content'])} chars retrieved")
        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["web_search", "file_search", "information_gathering", "research_synthesis"]
