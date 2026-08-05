from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import httpx

from core.configuration import settings

logger = logging.getLogger("superdev.ai.reasoning")


class ReasoningStrategy(str, Enum):
    STEP_BY_STEP = "step_by_step"
    TREE_OF_THOUGHT = "tree_of_thought"
    RECURSIVE_REFINEMENT = "recursive_refinement"
    DEBATE = "debate"
    REACT = "react"
    FEW_SHOT = "few_shot"


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: TokenUsage) -> TokenUsage:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        return self

    def reset(self) -> None:
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class ConversationTurn:
    role: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    token_usage: Optional[TokenUsage] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    answer: str
    strategy: ReasoningStrategy
    reasoning_path: list[str] = field(default_factory=list)
    confidence: float = 1.0
    token_usage: Optional[TokenUsage] = None
    duration_ms: float = 0.0
    intermediate_results: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self._api_key = api_key or settings.secret_key
        self._base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self._model = model or "gpt-4o"
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=httpx.Timeout(self._timeout),
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 1.0,
        stop: Optional[list[str]] = None,
    ) -> tuple[str, TokenUsage]:
        # Local offline fallback when no real API key is configured
        if not self._api_key or self._api_key in {
            "superdev-secret-key-change-in-production",
            "",
            "changeme",
        }:
            return self._local_completion(messages), TokenUsage()

        try:
            client = await self._get_client()
            body: dict[str, Any] = {
                "model": self._model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }
            if stop:
                body["stop"] = stop

            response = await client.post("/chat/completions", json=body)
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            content: str = choice["message"]["content"] or ""
            usage_data = data.get("usage", {})
            usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )
            return content, usage
        except Exception as exc:
            logger.warning("LLM request failed, using local fallback: %s", exc)
            return self._local_completion(messages), TokenUsage()

    def _local_completion(self, messages: list[dict[str, str]]) -> str:
        """Deterministic local reasoning when no external LLM is available."""
        user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"]
        prompt = user_msgs[-1] if user_msgs else ""
        system = next((m.get("content", "") for m in messages if m.get("role") == "system"), "")

        steps = [
            "1. Reformule o problema em termos claros.",
            f"2. Identifique os requisitos principais da solicitação: {prompt[:200]}",
            "3. Aponte uma abordagem prática de solução.",
            "4. Destaque riscos, casos extremos e etapas de validação.",
            "5. Forneça uma próxima ação concreta.",
        ]
        answer = (
            f"## Análise Local (modo offline)\n\n"
            f"**Solicitação:** {prompt[:500]}\n\n"
            f"### Caminho de raciocínio\n"
            + "\n".join(steps)
            + "\n\n### Recomendação\n"
            "Implemente a solução incrementalmente, valide com testes e proteja todas as entradas externas. "
            "Configure OPENAI_API_KEY para respostas completas com IA."
        )
        if "plan" in system.lower() or "plan" in prompt.lower() or "plano" in prompt.lower():
            answer += (
                "\n\n### Plano sugerido\n"
                "1. Requisitos e escopo\n"
                "2. Design da arquitetura\n"
                "3. Implementação\n"
                "4. Testes e revisão de segurança\n"
                "5. Implantação e monitoramento\n"
            )
        return answer

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


class ReasoningEngine:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        max_history: int = 100,
    ) -> None:
        self._llm = LLMClient(api_key=api_key, base_url=base_url, model=model)
        self._conversations: dict[str, list[ConversationTurn]] = {}
        self._max_history = max_history
        self._token_usage = TokenUsage()

    async def reason(
        self,
        prompt: str,
        strategy: ReasoningStrategy = ReasoningStrategy.STEP_BY_STEP,
        conversation_id: Optional[str] = None,
        context: Optional[list[dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ReasoningResult:
        start = time.monotonic()
        conv_id = conversation_id or uuid.uuid4().hex
        if conv_id not in self._conversations:
            self._conversations[conv_id] = []

        if strategy == ReasoningStrategy.STEP_BY_STEP:
            result = await self._step_by_step(conv_id, prompt, context, temperature, max_tokens)
        elif strategy == ReasoningStrategy.TREE_OF_THOUGHT:
            result = await self._tree_of_thought(conv_id, prompt, context, temperature, max_tokens)
        elif strategy == ReasoningStrategy.RECURSIVE_REFINEMENT:
            result = await self._recursive_refinement(conv_id, prompt, context, temperature, max_tokens)
        elif strategy == ReasoningStrategy.DEBATE:
            result = await self._debate(conv_id, prompt, context, temperature, max_tokens)
        elif strategy == ReasoningStrategy.REACT:
            result = await self._react(conv_id, prompt, context, temperature, max_tokens)
        elif strategy == ReasoningStrategy.FEW_SHOT:
            result = await self._few_shot(conv_id, prompt, context, temperature, max_tokens)
        else:
            result = await self._step_by_step(conv_id, prompt, context, temperature, max_tokens)

        result.duration_ms = (time.monotonic() - start) * 1000
        return result

    async def _step_by_step(
        self,
        conv_id: str,
        prompt: str,
        context: Optional[list[dict[str, str]]],
        temperature: float,
        max_tokens: int,
    ) -> ReasoningResult:
        system = {
            "role": "system",
            "content": "Você é um motor de raciocínio passo a passo. Decomponha seu raciocínio em etapas claras e numeradas. Mostre seu trabalho antes de dar a resposta final. Responda sempre em português do Brasil.",
        }
        messages = [system]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        content, usage = await self._llm.chat(messages, temperature, max_tokens)
        self._token_usage.add(usage)

        steps = [
            line.strip()
            for line in content.split("\n")
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-"))
        ]

        turn = ConversationTurn(role="assistant", content=content, token_usage=usage)
        self._conversations[conv_id].append(turn)
        self._trim_conversation(conv_id)

        return ReasoningResult(
            answer=content,
            strategy=ReasoningStrategy.STEP_BY_STEP,
            reasoning_path=steps or [content],
            confidence=self._estimate_confidence(content),
            token_usage=usage,
        )

    async def _tree_of_thought(
        self,
        conv_id: str,
        prompt: str,
        context: Optional[list[dict[str, str]]],
        temperature: float,
        max_tokens: int,
    ) -> ReasoningResult:
        system = {
            "role": "system",
            "content": "Você é um motor de raciocínio por árvore de pensamentos. Gere 3 abordagens distintas para resolver este problema. Para cada abordagem, explore o caminho de raciocínio. Depois selecione a melhor abordagem e forneça uma resposta final. Responda sempre em português do Brasil.",
        }
        messages = [system]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        content, usage = await self._llm.chat(messages, temperature, max_tokens)
        self._token_usage.add(usage)

        intermediate: list[dict[str, Any]] = []
        paths: list[str] = []
        current_path: list[str] = []

        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.lower().startswith("approach") or stripped.lower().startswith("path"):
                if current_path:
                    paths.append("\n".join(current_path))
                    current_path = []
                intermediate.append({"approach": stripped})
            elif stripped.lower().startswith("final answer"):
                if current_path:
                    paths.append("\n".join(current_path))
                    current_path = []
            else:
                if stripped:
                    current_path.append(stripped)

        if current_path:
            paths.append("\n".join(current_path))

        turn = ConversationTurn(role="assistant", content=content, token_usage=usage)
        self._conversations[conv_id].append(turn)
        self._trim_conversation(conv_id)

        return ReasoningResult(
            answer=content,
            strategy=ReasoningStrategy.TREE_OF_THOUGHT,
            reasoning_path=paths,
            confidence=self._estimate_confidence(content),
            token_usage=usage,
            intermediate_results=intermediate,
        )

    async def _recursive_refinement(
        self,
        conv_id: str,
        prompt: str,
        context: Optional[list[dict[str, str]]],
        temperature: float,
        max_tokens: int,
    ) -> ReasoningResult:
        system = {
            "role": "system",
            "content": "Você é um motor de refinamento recursivo. Primeiro forneça uma resposta inicial. Depois critique-a, identifique falhas e refine-a. Repita este processo de refinamento 3 vezes, mostrando cada iteração. Responda sempre em português do Brasil.",
        }
        messages = [system]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        content, usage = await self._llm.chat(messages, temperature, max_tokens)
        self._token_usage.add(usage)

        turn = ConversationTurn(role="assistant", content=content, token_usage=usage)
        self._conversations[conv_id].append(turn)
        self._trim_conversation(conv_id)

        iterations = content.split("Iteration")
        paths = [f"Iteration{it}" for it in iterations[1:]] if len(iterations) > 1 else [content]

        return ReasoningResult(
            answer=content,
            strategy=ReasoningStrategy.RECURSIVE_REFINEMENT,
            reasoning_path=paths,
            confidence=self._estimate_confidence(content),
            token_usage=usage,
        )

    async def _debate(
        self,
        conv_id: str,
        prompt: str,
        context: Optional[list[dict[str, str]]],
        temperature: float,
        max_tokens: int,
    ) -> ReasoningResult:
        messages: list[dict[str, str]] = []
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        perspectives = [
            "You are debating from a conservative, risk-averse perspective. Focus on stability and proven solutions.",
            "You are debating from an innovative, creative perspective. Focus on novel approaches and cutting-edge solutions.",
            "You are debating from a pragmatic, balanced perspective. Focus on practical tradeoffs and feasibility.",
        ]

        debate_rounds: list[str] = []
        for i, perspective in enumerate(perspectives):
            debate_msgs = [{"role": "system", "content": perspective}]
            debate_msgs.extend(messages)
            for prev in debate_rounds:
                debate_msgs.append({"role": "assistant", "content": prev})

            response_text, usage = await self._llm.chat(debate_msgs, temperature, max_tokens)
            self._token_usage.add(usage)
            debate_rounds.append(response_text)

        synthesis_prompt = {
            "role": "system",
            "content": "Você é um sintetizador de debates. Dados os seguintes argumentos de debate de múltiplas perspectivas, sintetize uma resposta final equilibrada que incorpore os melhores insights de cada perspectiva. Responda sempre em português do Brasil.",
        }
        synthesis_msgs = [synthesis_prompt]
        for i, round_text in enumerate(debate_rounds):
            synthesis_msgs.append({"role": "user", "content": f"Perspective {i+1}: {round_text}"})
        synthesis_msgs.append({"role": "user", "content": "Synthesize these perspectives into a final answer."})

        final, usage = await self._llm.chat(synthesis_msgs, temperature, max_tokens)
        self._token_usage.add(usage)

        turn = ConversationTurn(role="assistant", content=final, token_usage=usage)
        self._conversations[conv_id].append(turn)
        self._trim_conversation(conv_id)

        return ReasoningResult(
            answer=final,
            strategy=ReasoningStrategy.DEBATE,
            reasoning_path=debate_rounds + [final],
            confidence=self._estimate_confidence(final),
            token_usage=usage,
            intermediate_results=[{"perspective": p, "argument": a} for p, a in zip(perspectives, debate_rounds)],
        )

    async def _react(
        self,
        conv_id: str,
        prompt: str,
        context: Optional[list[dict[str, str]]],
        temperature: float,
        max_tokens: int,
    ) -> ReasoningResult:
        system = {
            "role": "system",
            "content": "Você é um motor ReAct (Raciocínio + Ação). Para cada etapa, produza:\nPensamento: <seu raciocínio>\nAção: <o que fazer>\nObservação: <resultado>\nContinue este ciclo até chegar a uma resposta final, então produza:\nResposta Final: <resposta>. Responda sempre em português do Brasil.",
        }
        messages = [system]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        content, usage = await self._llm.chat(messages, temperature, max_tokens)
        self._token_usage.add(usage)

        turn = ConversationTurn(role="assistant", content=content, token_usage=usage)
        self._conversations[conv_id].append(turn)
        self._trim_conversation(conv_id)

        steps: list[str] = []
        for line in content.split("\n"):
            stripped = line.strip()
            if any(stripped.lower().startswith(prefix) for prefix in ("thought:", "action:", "observation:", "final answer:")):
                steps.append(stripped)

        return ReasoningResult(
            answer=content,
            strategy=ReasoningStrategy.REACT,
            reasoning_path=steps or [content],
            confidence=self._estimate_confidence(content),
            token_usage=usage,
        )

    async def _few_shot(
        self,
        conv_id: str,
        prompt: str,
        context: Optional[list[dict[str, str]]],
        temperature: float,
        max_tokens: int,
    ) -> ReasoningResult:
        examples = context or [
            {"role": "user", "content": "Solve: What is 15 * 7?"},
            {"role": "assistant", "content": "15 * 7 = 105. Step 1: 10 * 7 = 70. Step 2: 5 * 7 = 35. Step 3: 70 + 35 = 105."},
        ]
        messages = [
            {"role": "system", "content": "Use os seguintes exemplos para guiar sua abordagem de raciocínio. Siga o mesmo padrão. Responda sempre em português do Brasil."},
            *examples,
            {"role": "user", "content": prompt},
        ]

        content, usage = await self._llm.chat(messages, temperature, max_tokens)
        self._token_usage.add(usage)

        turn = ConversationTurn(role="assistant", content=content, token_usage=usage)
        self._conversations[conv_id].append(turn)
        self._trim_conversation(conv_id)

        return ReasoningResult(
            answer=content,
            strategy=ReasoningStrategy.FEW_SHOT,
            reasoning_path=[content],
            confidence=self._estimate_confidence(content),
            token_usage=usage,
        )

    def _estimate_confidence(self, response: str) -> float:
        certainty_indicators = ["i am certain", "definitely", "clearly", "without doubt", "conclusively", "always"]
        uncertainty_indicators = ["i think", "maybe", "perhaps", "possibly", "might be", "could be", "not sure", "uncertain", "unclear", "i'm not sure"]

        lower = response.lower()
        certainty_score = sum(1 for ind in certainty_indicators if ind in lower)
        uncertainty_score = sum(1 for ind in uncertainty_indicators if ind in lower)

        base = 0.8
        adjustment = (certainty_score * 0.05) - (uncertainty_score * 0.1)
        return max(0.1, min(1.0, base + adjustment))

    def _trim_conversation(self, conv_id: str) -> None:
        if len(self._conversations[conv_id]) > self._max_history:
            self._conversations[conv_id] = self._conversations[conv_id][-self._max_history:]

    async def chat(
        self,
        message: str,
        conversation_id: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        history = self._conversations[conversation_id]
        for turn in history:
            messages.append({"role": turn.role, "content": turn.content})

        messages.append({"role": "user", "content": message})

        content, usage = await self._llm.chat(messages, temperature, max_tokens)
        self._token_usage.add(usage)

        self._conversations[conversation_id].append(ConversationTurn(role="user", content=message))
        self._conversations[conversation_id].append(
            ConversationTurn(role="assistant", content=content, token_usage=usage)
        )
        self._trim_conversation(conversation_id)

        return content

    def get_conversation_history(self, conversation_id: str) -> list[ConversationTurn]:
        return list(self._conversations.get(conversation_id, []))

    def clear_conversation(self, conversation_id: str) -> None:
        self._conversations.pop(conversation_id, None)

    def clear_all_conversations(self) -> None:
        self._conversations.clear()

    def get_token_usage(self) -> TokenUsage:
        return self._token_usage

    def reset_token_usage(self) -> None:
        self._token_usage.reset()

    async def set_model(self, model: str) -> None:
        await self._llm.close()
        self._llm = LLMClient(model=model)

    async def close(self) -> None:
        await self._llm.close()
