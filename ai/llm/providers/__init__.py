from __future__ import annotations

"""LLM provider implementations — real SDKs and OpenAI-compatible APIs."""

from .anthropic_provider import AnthropicProvider
from .aws_provider import AWSBedrockProvider
from .azure_provider import AzureOpenAIProvider
from .base_provider import BaseLLMProvider
from .cohere_provider import CohereProvider
from .custom_provider import CustomProvider
from .deepseek_provider import DeepSeekProvider
from .google_provider import GoogleProvider
from .groq_provider import GroqProvider
from .huggingface_provider import HuggingFaceProvider
from .local_provider import LocalProvider
from .mistral_provider import MistralProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider
from .together_provider import TogetherProvider

# --- Provider class map for factory registration ---

PROVIDER_CLASSES: dict[str, type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "deepseek": DeepSeekProvider,
    "groq": GroqProvider,
    "mistral": MistralProvider,
    "together": TogetherProvider,
    "azure": AzureOpenAIProvider,
    "aws": AWSBedrockProvider,
    "cohere": CohereProvider,
    "huggingface": HuggingFaceProvider,
    "local": LocalProvider,
    "mock": MockProvider,
    "custom": CustomProvider,
}

# --- Default env var mappings for auto-discovery ---

PROVIDER_ENV_MAP: dict[str, dict[str, str]] = {
    "openai": {"api_key": "OPENAI_API_KEY", "base_url": "OPENAI_BASE_URL"},
    "anthropic": {"api_key": "ANTHROPIC_API_KEY", "base_url": "ANTHROPIC_BASE_URL"},
    "google": {"api_key": "GEMINI_API_KEY"},
    "deepseek": {"api_key": "DEEPSEEK_API_KEY"},
    "groq": {"api_key": "GROQ_API_KEY"},
    "mistral": {"api_key": "MISTRAL_API_KEY"},
    "together": {"api_key": "TOGETHER_API_KEY"},
    "azure": {"api_key": "AZURE_OPENAI_API_KEY"},
    "aws": {"api_key": "AWS_ACCESS_KEY_ID"},
    "cohere": {"api_key": "COHERE_API_KEY"},
    "huggingface": {"api_key": "HUGGINGFACE_API_KEY"},
}

# --- Default model per provider ---

PROVIDER_DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
    "google": "gemini-2.0-flash",
    "deepseek": "deepseek-chat",
    "groq": "llama-3.3-70b-versatile",
    "mistral": "mistral-large-latest",
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "azure": "gpt-4o",
    "aws": "claude-3-5-sonnet-20241022",
    "cohere": "command-r-plus",
    "huggingface": "HuggingFaceH4/zephyr-7b-beta",
    "local": "local-model",
    "mock": "mock-model",
    "custom": "custom-model",
}

__all__ = [
    "AnthropicProvider",
    "AWSBedrockProvider",
    "AzureOpenAIProvider",
    "BaseLLMProvider",
    "CohereProvider",
    "CustomProvider",
    "DeepSeekProvider",
    "GoogleProvider",
    "GroqProvider",
    "HuggingFaceProvider",
    "LocalProvider",
    "MistralProvider",
    "MockProvider",
    "OpenAIProvider",
    "TogetherProvider",
    "PROVIDER_CLASSES",
    "PROVIDER_ENV_MAP",
    "PROVIDER_DEFAULT_MODELS",
]
