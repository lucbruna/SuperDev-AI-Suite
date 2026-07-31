from ..cache.prompt_cache import PromptCache
from ..conversations.conversation import ConversationManager
from ..cost.cost_tracker import CostTracker
from ..embeddings.embedding_manager import EmbeddingManager
from ..providers.provider_factory import ProviderFactory
from ..providers.provider_manager import ProviderManager
from ..routing.router import AIRouter
from ..sessions.session import SessionManager
from ..streaming.stream_manager import StreamManager
from .configuration import AIPlatformConfig, get_platform_config
from .kernel import AIKernel


class AIPlatform:
    def __init__(self, config: AIPlatformConfig | None = None):
        self.config = config or get_platform_config()
        self.kernel = AIKernel(self.config)
        self.provider_manager = ProviderManager()
        self.provider_factory = ProviderFactory()
        self.router = AIRouter()
        self.stream_manager = StreamManager()
        self.session_manager = SessionManager()
        self.conversation_manager = ConversationManager()
        self.cost_tracker = CostTracker()
        self.cache = PromptCache()
        self.embedding_manager = EmbeddingManager()
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        provider_configs = self.kernel.bootstrap()
        self.provider_manager.initialize_all(provider_configs)
        await self.cache.initialize()
        self._initialized = True

    async def shutdown(self) -> None:
        if not self._initialized:
            return
        active = self.stream_manager.list_active_streams()
        for sid in list(active.keys()):
            await self.stream_manager.cancel_stream(sid)
        self._initialized = False

    def get_provider(self, name: str):
        return self.provider_manager.get_provider(name)

    async def chat(self, messages: list[dict], provider: str | None = None, model: str | None = None, **kwargs):
        cache_key = self.cache.cache_key(messages, model or "", kwargs)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        p, m = self.router.route(messages, {"provider": provider, "model": model})
        prov = self.provider_manager.get_provider(p)
        response = await prov.chat(messages, {**kwargs, "model": m})
        await self.cache.set(cache_key, response)
        return response

    async def stream(self, messages: list[dict], provider: str | None = None, model: str | None = None, **kwargs):
        p, m = self.router.route(messages, {"provider": provider, "model": model})
        prov = self.provider_manager.get_provider(p)
        stream_id = self.stream_manager.create_stream(prov, messages, {**kwargs, "model": m})
        try:
            async for chunk in prov.stream(messages, {**kwargs, "model": m}):
                yield chunk
        finally:
            await self.stream_manager.cancel_stream(stream_id)

    async def embeddings(self, texts: list[str], provider: str | None = None):
        return await self.embedding_manager.embed_texts(texts, provider, self.provider_manager)
