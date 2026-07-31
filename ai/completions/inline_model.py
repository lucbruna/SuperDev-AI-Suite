from __future__ import annotations

import os
from typing import Any

import httpx


class InlineCompletionModel:
    def __init__(self, model_name: str = "gpt-4o-mini", base_url: str | None = None):
        self.model_name = model_name
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self._base_url = base_url or "https://api.openai.com/v1"

    async def predict(self, prefix: str, suffix: str = "", language: str = "python", max_tokens: int = 64) -> dict[str, Any]:
        if not self._api_key:
            return self._local_fallback(prefix, language)
        prompt = self._build_prompt(prefix, suffix, language)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.2,
                        "stop": ["\n\n"],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"].strip()
                return {"completion": text, "model": self.model_name, "tokens": data["usage"]["total_tokens"], "source": "ai"}
        except Exception:
            return self._local_fallback(prefix, language)

    async def predict_batch(self, contexts: list[tuple[str, str, str]]) -> list[dict[str, Any]]:
        import asyncio
        tasks = [self.predict(prefix, suffix, lang) for prefix, suffix, lang in contexts]
        return await asyncio.gather(*tasks)

    def _build_prompt(self, prefix: str, suffix: str, language: str) -> str:
        parts = [f"Complete the following {language} code. Only return the completion, no explanation."]
        if prefix:
            parts.append(f"\n```{language}\n{prefix}")
        if suffix:
            parts.append(f"\n{'─' * 40}\nCursor is here. Complete the code after this point:\n{suffix}")
        parts.append("\n```\nCompletion:")
        return "\n".join(parts)

    def _local_fallback(self, prefix: str, language: str) -> dict[str, Any]:
        last_line = prefix.strip().split("\n")[-1] if prefix.strip() else ""
        common = {
            "def ": "    pass\n",
            "class ": "    pass\n",
            "import ": "",
            "from ": "",
            "if __name__": "    main()\n",
            "# TODO": " implement\n",
            "return": " None\n",
        }
        for key, val in common.items():
            if last_line.startswith(key):
                return {"completion": val, "model": "fallback", "tokens": 0, "source": "local"}
        return {"completion": "", "model": "fallback", "tokens": 0, "source": "local"}
