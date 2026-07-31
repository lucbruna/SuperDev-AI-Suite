from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from typing import Any

from .base_provider import (
    BaseLLMProvider,
    PricingRow,
    ProviderError,
    ProviderErrorCode,
    StreamDelta,
    _exponential_backoff,
    _is_retryable,
    count_tokens,
)

# ---------------------------------------------------------------------------
# Pricing (per 1K tokens, USD)
# ---------------------------------------------------------------------------

BEDROCK_PRICING: dict[str, PricingRow] = {
    # Anthropic Claude on Bedrock
    "anthropic.claude-3-5-sonnet-20241022-v2:0": PricingRow(0.003, 0.015),
    "anthropic.claude-3-opus-20240229-v1:0": PricingRow(0.015, 0.075),
    "anthropic.claude-3-sonnet-20240229-v1:0": PricingRow(0.003, 0.015),
    "anthropic.claude-3-haiku-20240307-v1:0": PricingRow(0.00025, 0.00125),
    "anthropic.claude-2.1-v1:0": PricingRow(0.008, 0.024),
    "anthropic.claude-2.0-v1:0": PricingRow(0.008, 0.024),
    "anthropic.claude-instant-1.2-v1:0": PricingRow(0.0008, 0.0024),
    # Meta Llama
    "meta.llama3-70b-instruct-v1:0": PricingRow(0.00265, 0.00356),
    "meta.llama3-8b-instruct-v1:0": PricingRow(0.0004, 0.00056),
    "meta.llama3-1-70b-instruct-v1:0": PricingRow(0.00265, 0.00356),
    "meta.llama3-1-8b-instruct-v1:0": PricingRow(0.0004, 0.00056),
    # Mistral
    "mistral.mistral-large-2402-v1:0": PricingRow(0.004, 0.012),
    "mistral.mistral-7b-instruct-v0:2": PricingRow(0.00015, 0.00015),
    # Amazon Titan
    "amazon.titan-text-premier-v1:0": PricingRow(0.0005, 0.0015),
    "amazon.titan-text-lite-v1:0": PricingRow(0.0003, 0.0004),
    "amazon.titan-text-express-v1:0": PricingRow(0.0008, 0.0016),
}

BEDROCK_CONVERSE_MODELS: set[str] = {
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-2.1-v1:0",
    "anthropic.claude-2.0-v1:0",
    "anthropic.claude-instant-1.2-v1:0",
    "meta.llama3-70b-instruct-v1:0",
    "meta.llama3-8b-instruct-v1:0",
    "meta.llama3-1-70b-instruct-v1:0",
    "meta.llama3-1-8b-instruct-v1:0",
    "mistral.mistral-large-2402-v1:0",
    "mistral.mistral-7b-instruct-v0:2",
    "mistral.mixtral-8x7b-instruct-v0:1",
}

# Map short names to full Bedrock model IDs
BEDROCK_MODEL_ALIAS: dict[str, str] = {
    "claude-3-5-sonnet": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "claude-3-5-sonnet-20241022": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "claude-3-opus": "anthropic.claude-3-opus-20240229-v1:0",
    "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "claude-2": "anthropic.claude-2.1-v1:0",
    "claude-instant": "anthropic.claude-instant-1.2-v1:0",
    "llama3-70b": "meta.llama3-70b-instruct-v1:0",
    "llama3-8b": "meta.llama3-8b-instruct-v1:0",
    "llama-3.1-70b": "meta.llama3-1-70b-instruct-v1:0",
    "llama-3.1-8b": "meta.llama3-1-8b-instruct-v1:0",
    "mistral-large": "mistral.mistral-large-2402-v1:0",
    "mistral-7b": "mistral.mistral-7b-instruct-v0:2",
    "mixtral-8x7b": "mistral.mixtral-8x7b-instruct-v0:1",
    "titan-text-premier": "amazon.titan-text-premier-v1:0",
    "titan-text-lite": "amazon.titan-text-lite-v1:0",
    "titan-text-express": "amazon.titan-text-express-v1:0",
}


def _resolve_bedrock_model(model: str) -> str:
    """Resolve a short model name to a full Bedrock model ID."""
    if (
        model.startswith("anthropic.")
        or model.startswith("meta.")
        or model.startswith("mistral.")
        or model.startswith("amazon.")
    ):
        return model
    resolved = BEDROCK_MODEL_ALIAS.get(model)
    if resolved:
        return resolved
    # If it contains a period assume it's already a full model ID
    if "." in model:
        return model
    return model


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class AWSBedrockProvider(BaseLLMProvider):
    """AWS Bedrock provider using the boto3 SDK with the Converse API.

    Supports:
    - Anthropic Claude 3/3.5 (Converse API)
    - Meta Llama 3/3.1 (Converse API)
    - Mistral / Mixtral (Converse API)
    - Amazon Titan (invoke_model fallback)
    - Streaming (Converse Stream API)
    - Tool calling (Converse API)
    - Automatic retry and rate limiting
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet",
        region: str = "",
        access_key: str = "",
        secret_key: str = "",
        session_token: str = "",
        max_retries: int = 3,
        requests_per_minute: int = 500,
    ) -> None:
        resolved = _resolve_bedrock_model(model)
        super().__init__(name="aws", model=resolved)
        self._original_model = model  # keep the original alias for to_dict
        self._region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self._access_key = access_key or os.getenv("AWS_ACCESS_KEY_ID", "")
        self._secret_key = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self._session_token = session_token or os.getenv("AWS_SESSION_TOKEN", "")
        self._max_retries = max_retries
        self._pricing = BEDROCK_PRICING
        self._client: Any = None
        if self._access_key:
            self.set_rate_limit(requests_per_minute)
        self._supports_converse = resolved in BEDROCK_CONVERSE_MODELS or any(
            resolved.startswith(prefix)
            for prefix in (
                "anthropic.claude-3-5",
                "anthropic.claude-3-",
                "anthropic.claude-2",
                "anthropic.claude-instant",
                "meta.llama3-",
                "meta.llama3-1-",
                "mistral.",
            )
        )

    # ── Client ──────────────────────────────────────────────────────

    def _get_client(self):
        if self._client is None:
            try:
                import aioboto3
                import botocore.config

                botocore.config.Config(
                    retries={"max_attempts": 0, "mode": "standard"},
                    connect_timeout=30,
                    read_timeout=120,
                )

                self._session = aioboto3.Session(
                    aws_access_key_id=self._access_key or None,
                    aws_secret_access_key=self._secret_key or None,
                    aws_session_token=self._session_token or None,
                    region_name=self._region,
                )
                # We create clients per-call via _get_async_client()
            except ImportError:
                raise ProviderError(
                    ProviderErrorCode.API_ERROR,
                    "aioboto3 library required. pip install aioboto3 botocore",
                    provider="aws",
                )
        return self._session

    async def _get_async_client(self):
        """Create an async bedrock-runtime client for each call."""
        session = self._get_client()
        return await session.client("bedrock-runtime", region_name=self._region).__aenter__()

    # ── ILLMProvider ────────────────────────────────────────────────

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return await self._execute_with_retry(self._generate, prompt, **kwargs)

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _stream() -> AsyncIterator[dict[str, Any]]:
            attempt = 0
            while attempt <= self._max_retries:
                try:
                    await self._throttle()
                    async for chunk in self._consume_stream(prompt, **kwargs):
                        yield chunk
                    break
                except ProviderError as e:
                    attempt += 1
                    if attempt > self._max_retries or not _is_retryable(e, self._retry_codes):
                        yield {
                            "content": f"[{self._name} error: {e.message}]",
                            "finish_reason": "error",
                            "error": e.message,
                        }
                        break
                    retry_after = e.retry_after or _exponential_backoff(attempt - 1)
                    await asyncio.sleep(retry_after)
                except Exception as e:
                    pe = ProviderError.from_exception(e, self._name)
                    attempt += 1
                    if attempt > self._max_retries or not _is_retryable(pe, self._retry_codes):
                        yield {
                            "content": f"[{self._name} error: {pe.message}]",
                            "finish_reason": "error",
                            "error": pe.message,
                        }
                        break
                    await asyncio.sleep(_exponential_backoff(attempt - 1))

        return _stream()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    # ── Internal generation ─────────────────────────────────────────

    async def _generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        model = _resolve_bedrock_model(kwargs.get("model") or self._model)
        use_converse = self._supports_converse or model in BEDROCK_CONVERSE_MODELS

        if use_converse:
            return await self._generate_converse(prompt, model, kwargs)
        else:
            return await self._generate_invoke(prompt, model, kwargs)

    async def _generate_converse(self, prompt: str, model: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        client = await self._get_async_client()
        try:
            messages = self._build_converse_messages(prompt, kwargs)
            system_content = self._build_system_content(kwargs)
            inference_config = self._build_inference_config(kwargs)

            body: dict[str, Any] = {
                "modelId": model,
                "messages": messages,
                "inferenceConfig": inference_config,
            }
            if system_content:
                body["system"] = system_content

            tools = kwargs.get("tools")
            if tools:
                body["toolConfig"] = self._convert_tools(tools)

            resp = await client.converse(**body)
        except Exception as e:
            raise self._classify_error(e)
        finally:
            await client.__aexit__(None, None, None)

        return self._parse_converse_response(resp, prompt)

    async def _generate_invoke(self, prompt: str, model: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Fallback for models that don't support the Converse API (e.g., Titan)."""
        client = await self._get_async_client()
        try:
            # Titan text format
            body = json.dumps(
                {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": kwargs.get("max_tokens", 4096),
                        "temperature": kwargs.get("temperature", 0.7),
                        "topP": kwargs.get("top_p", 1.0),
                    },
                }
            )

            resp = await client.invoke_model(
                modelId=model,
                contentType="application/json",
                accept="application/json",
                body=body,
            )

            response_body = json.loads(await resp["body"].read())
            content = response_body.get("results", [{}])[0].get("outputText", "")
            pt = count_tokens(prompt)
            ct = count_tokens(content)

            return {
                "content": content,
                "success": True,
                "finish_reason": "stop",
                **self._track_usage(pt, ct),
            }
        except Exception as e:
            raise self._classify_error(e)
        finally:
            await client.__aexit__(None, None, None)

    # ── Streaming ───────────────────────────────────────────────────

    async def _consume_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        model = _resolve_bedrock_model(kwargs.get("model") or self._model)

        if not self._supports_converse and model not in BEDROCK_CONVERSE_MODELS:
            # Non-streaming fallback for non-Converse models
            result = await self._generate(prompt, **kwargs)
            yield result
            return

        client = await self._get_async_client()
        try:
            messages = self._build_converse_messages(prompt, kwargs)
            system_content = self._build_system_content(kwargs)
            inference_config = self._build_inference_config(kwargs)

            body: dict[str, Any] = {
                "modelId": model,
                "messages": messages,
                "inferenceConfig": inference_config,
            }
            if system_content:
                body["system"] = system_content

            tools = kwargs.get("tools")
            if tools:
                body["toolConfig"] = self._convert_tools(tools)

            response = await client.converse_stream(**body)
            stream = response.get("stream")

            if stream is None:
                # Fallback via non-streaming converse
                result = await self._generate_converse(prompt, model, kwargs)
                yield result
                return

            async for event in stream:
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"]["delta"]
                    if "text" in delta:
                        yield {
                            "content": delta["text"],
                            "finish_reason": None,
                            "delta": StreamDelta(content=delta["text"]),
                        }

                elif "messageStop" in event:
                    stop_reason = event["messageStop"].get("stopReason", "stop")
                    yield {
                        "content": "",
                        "finish_reason": stop_reason,
                        "delta": StreamDelta(finish_reason=stop_reason),
                    }

                elif "metadata" in event:
                    metadata = event["metadata"]
                    if "usage" in metadata:
                        u = metadata["usage"]
                        {
                            "prompt_tokens": u.get("inputTokens", 0),
                            "completion_tokens": u.get("outputTokens", 0),
                            "total_tokens": u.get("totalTokens", 0),
                        }
                        self._track_usage(u.get("inputTokens", 0), u.get("outputTokens", 0))

                elif "internalServerException" in event:
                    raise ProviderError(
                        ProviderErrorCode.SERVER_ERROR,
                        event["internalServerException"].get("message", "Internal server error"),
                        provider="aws",
                    )
                elif "modelStreamErrorException" in event:
                    raise self._classify_error(
                        Exception(event["modelStreamErrorException"].get("message", "Model stream error"))
                    )

        except Exception as e:
            if not isinstance(e, ProviderError):
                raise ProviderError.from_exception(e, "aws")
            raise
        finally:
            await client.__aexit__(None, None, None)

    # ── Response parsing ────────────────────────────────────────────

    def _parse_converse_response(self, resp: dict[str, Any], prompt: str) -> dict[str, Any]:
        output = resp.get("output", {})
        message = output.get("message", {})
        content_parts = message.get("content", [])

        # Extract text content
        text_parts = [p.get("text", "") for p in content_parts if "text" in p]
        content = "".join(text_parts)

        # Extract tool calls
        tool_calls = None
        tool_parts = [p for p in content_parts if "toolUse" in p]
        if tool_parts:
            tool_calls = []
            for tp in tool_parts:
                tu = tp["toolUse"]
                tool_calls.append(
                    {
                        "id": tu.get("toolUseId", ""),
                        "type": "function",
                        "function": {
                            "name": tu.get("name", ""),
                            "arguments": json.dumps(tu.get("input", {})),
                        },
                    }
                )

        stop_reason_raw = output.get("stopReason", "stop")
        finish_reason = {
            "end_turn": "stop",
            "tool_use": "tool_calls",
            "max_tokens": "length",
            "content_filtered": "content_filter",
            "stop_sequence": "stop",
        }.get(stop_reason_raw, stop_reason_raw)

        usage = resp.get("usage", {})
        pt = usage.get("inputTokens", count_tokens(prompt))
        ct = usage.get("outputTokens", count_tokens(content))

        result: dict[str, Any] = {
            "content": content,
            "success": True,
            "finish_reason": finish_reason,
            **self._track_usage(pt, ct),
        }
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    # ── Builders ─────────────────────────────────────────────────────

    def _build_converse_messages(self, prompt: str, kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []

        chat_history = kwargs.get("messages", [])
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Convert string content to Converse content blocks
            if isinstance(content, str):
                content = [{"text": content}]
            messages.append({"role": role if role != "system" else "user", "content": content})

        # Add current prompt
        messages.append(
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        )

        return messages

    def _build_system_content(self, kwargs: dict[str, Any]) -> list[dict[str, Any]] | None:
        system = kwargs.get("system")
        if system:
            return [{"text": system}]
        return None

    def _build_inference_config(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        config: dict[str, Any] = {}
        if "max_tokens" in kwargs:
            config["maxTokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            config["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            config["topP"] = kwargs["top_p"]
        if "stop_sequences" in kwargs:
            config["stopSequences"] = kwargs["stop_sequences"]
        return config

    def _convert_tools(self, tools: list[dict[str, Any]]) -> dict[str, Any]:
        """Convert OpenAI-style tools to Bedrock tool configuration."""
        bedrock_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                fn = tool["function"]
                bedrock_tools.append(
                    {
                        "toolSpec": {
                            "name": fn.get("name", ""),
                            "description": fn.get("description", ""),
                            "inputSchema": {
                                "json": fn.get("parameters", {}),
                            },
                        }
                    }
                )
        return {"tools": bedrock_tools}

    # ── Error classification ────────────────────────────────────────

    def _classify_error(self, exc: Exception) -> ProviderError:
        msg = str(exc).lower()

        if "accessdenied" in msg or "unauthorized" in msg or "access denied" in msg:
            return ProviderError(ProviderErrorCode.AUTH, str(exc), 403, provider="aws")
        if "throttling" in msg or "toomanyrequests" in msg or "429" in msg:
            return ProviderError(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider="aws")
        if "modelnotready" in msg or "validation" in msg:
            return ProviderError(ProviderErrorCode.INVALID_REQUEST, str(exc), 400, provider="aws")
        if "timeout" in msg or "timed out" in msg:
            return ProviderError(ProviderErrorCode.TIMEOUT, str(exc), 408, provider="aws")
        if "modelstreamerror" in msg or "internal" in msg:
            return ProviderError(ProviderErrorCode.SERVER_ERROR, str(exc), 500, provider="aws")
        if "max_token" in msg or "context length" in msg:
            return ProviderError(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider="aws")

        return ProviderError(ProviderErrorCode.API_ERROR, str(exc), 0, provider="aws")

    # ── Health ───────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        import time as time_module

        start = time_module.monotonic()
        try:
            client = await self._get_async_client()
            try:
                # List foundation models as health check
                await client.list_foundation_models()
                elapsed = (time_module.monotonic() - start) * 1000
                return {
                    "status": "healthy",
                    "latency_ms": round(elapsed, 1),
                    "provider": "aws",
                    "model": self._model,
                    "region": self._region,
                }
            finally:
                await client.__aexit__(None, None, None)
        except Exception as e:
            elapsed = (time_module.monotonic() - start) * 1000
            return {"status": "unhealthy", "latency_ms": round(elapsed, 1), "error": str(e), "provider": "aws"}

    # ── Models ───────────────────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "capabilities": ["chat", "vision", "tools"],
                "context_window": 200000,
            },
            {
                "id": "anthropic.claude-3-opus-20240229-v1:0",
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "capabilities": ["chat", "vision", "tools"],
                "context_window": 200000,
            },
            {
                "id": "anthropic.claude-3-haiku-20240307-v1:0",
                "name": "Claude 3 Haiku",
                "provider": "Anthropic",
                "capabilities": ["chat", "vision", "tools"],
                "context_window": 200000,
            },
            {
                "id": "meta.llama3-1-70b-instruct-v1:0",
                "name": "Llama 3.1 70B",
                "provider": "Meta",
                "capabilities": ["chat", "tools"],
                "context_window": 128000,
            },
            {
                "id": "meta.llama3-1-8b-instruct-v1:0",
                "name": "Llama 3.1 8B",
                "provider": "Meta",
                "capabilities": ["chat", "tools"],
                "context_window": 128000,
            },
            {
                "id": "mistral.mistral-large-2402-v1:0",
                "name": "Mistral Large",
                "provider": "Mistral",
                "capabilities": ["chat", "tools"],
                "context_window": 32000,
            },
            {
                "id": "amazon.titan-text-premier-v1:0",
                "name": "Titan Text Premier",
                "provider": "Amazon",
                "capabilities": ["chat"],
                "context_window": 32000,
            },
        ]

    # ── Cleanup ──────────────────────────────────────────────────────

    async def cleanup(self) -> None:
        self._client = None

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["region"] = self._region
        base["model_id"] = self._model
        base["original_model"] = self._original_model
        base["supports_converse"] = self._supports_converse
        return base
