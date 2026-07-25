from __future__ import annotations

import json

from ..providers.base_provider import StreamChunk, Usage


class StreamParser:
    @staticmethod
    def parse_openai_chunk(raw: str) -> StreamChunk | None:
        if not raw.startswith("data: "):
            return None
        payload = raw[6:].strip()
        if payload == "[DONE]":
            return StreamChunk(delta="", finish_reason="stop")
        try:
            data = json.loads(payload)
            choices = data.get("choices", [])
            if not choices:
                return None
            delta = choices[0].get("delta", {})
            content = delta.get("content", "")
            finish = choices[0].get("finish_reason")
            usage_data = data.get("usage")
            usage = None
            if usage_data:
                usage = Usage(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                )
            return StreamChunk(
                delta=content,
                finish_reason=finish,
                usage=usage,
                model=data.get("model", ""),
            )
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    @staticmethod
    def parse_anthropic_chunk(raw: str) -> StreamChunk | None:
        if not raw.startswith("data: "):
            return None
        payload = raw[6:].strip()
        try:
            data = json.loads(payload)
            typ = data.get("type", "")
            if typ == "content_block_delta":
                delta = data.get("delta", {})
                text = delta.get("text", "")
                return StreamChunk(delta=text)
            elif typ == "message_stop":
                return StreamChunk(delta="", finish_reason="stop")
            elif typ == "error":
                return StreamChunk(delta=f"[Error: {data.get('error', {}).get('message', 'unknown')}]", finish_reason="error")
            return None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def parse_ollama_chunk(raw: str) -> StreamChunk | None:
        if not raw.strip():
            return None
        try:
            data = json.loads(raw)
            if data.get("done"):
                return StreamChunk(delta="", finish_reason="stop")
            content = data.get("message", {}).get("content", "")
            if content:
                return StreamChunk(delta=content)
            return None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def parse_chunk(raw: str, source: str = "openai") -> StreamChunk | None:
        parsers = {
            "openai": StreamParser.parse_openai_chunk,
            "anthropic": StreamParser.parse_anthropic_chunk,
            "ollama": StreamParser.parse_ollama_chunk,
        }
        parser = parsers.get(source)
        if parser:
            return parser(raw)
        return StreamParser.parse_openai_chunk(raw)
