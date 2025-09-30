"""High-level service for interacting with configured LLM providers."""

from __future__ import annotations

import asyncio
import dataclasses
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from .base import LLMClient, LLMClientError, LLMMessage, LLMRateLimitError, LLMResponse, ensure_messages
from .providers import OpenAICompatibleClient

_DEFAULT_LM_PROXY_BASE_URL = "http://localhost:11434/v1"


@dataclass(slots=True)
class ProviderConfig:
    """Configuration for a single LLM provider entry."""

    name: str
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "Authorization"
    timeout: int = 30
    max_retries: int = 3
    extra_headers: Dict[str, str] = field(default_factory=dict)
    provider_label: Optional[str] = None


@dataclass(slots=True)
class LLMServiceConfig:
    """Configuration for the LLM service including fallbacks."""

    primary: ProviderConfig
    fallbacks: List[ProviderConfig] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "LLMServiceConfig":
        """Load configuration from environment variables."""

        primary_name = os.getenv("SCRAI_LLM_PROVIDER", "openrouter")
        model = os.getenv("SCRAI_LLM_MODEL")
        base_url = os.getenv("SCRAI_LLM_BASE_URL")
        api_key = os.getenv("SCRAI_LLM_API_KEY")
        timeout = int(os.getenv("SCRAI_LLM_TIMEOUT", "30"))
        max_retries = int(os.getenv("SCRAI_LLM_MAX_RETRIES", "3"))

        primary = ProviderConfig(
            name=primary_name,
            model=model,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

        return cls(primary=primary)


class LLMService:
    """Facade that provides easy access to configured LLM providers."""

    def __init__(self, config: LLMServiceConfig) -> None:
        self._config = config
        self._clients: Dict[str, LLMClient] = {}
        self._lock = asyncio.Lock()

    async def complete(
        self,
        messages: Iterable[LLMMessage | Mapping[str, str]],
        *,
        provider: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate a completion using the configured providers with fallbacks."""

        normalized = ensure_messages(messages)
        providers = self._provider_sequence(provider)
        last_error: Optional[Exception] = None

        for provider_config in providers:
            client = await self._get_or_create_client(provider_config)
            try:
                return await client.generate_response(normalized, **kwargs)
            except (LLMRateLimitError, LLMClientError) as exc:
                last_error = exc
                continue

        if last_error:
            raise last_error
        raise RuntimeError("No LLM providers are configured")

    async def list_models(self, provider: Optional[str] = None) -> List[str]:
        """List models from the specified provider (or primary by default)."""

        provider_config = self._select_provider(provider)
        client = await self._get_or_create_client(provider_config)
        return await client.list_models()

    async def validate(self) -> bool:
        """Validate all configured providers."""

        is_valid = True
        for provider_config in self._provider_sequence():
            try:
                client = await self._get_or_create_client(provider_config)
                if not await client.validate_connection():
                    is_valid = False
            except (LLMClientError, LLMRateLimitError):
                is_valid = False
        return is_valid

    async def close(self) -> None:
        """Close all underlying client sessions."""

        for client in self._clients.values():
            await client.close()
        self._clients.clear()

    def _provider_sequence(self, preferred: Optional[str] = None) -> Sequence[ProviderConfig]:
        if preferred:
            for cfg in [self._config.primary, *self._config.fallbacks]:
                if cfg.name == preferred:
                    return [cfg]
            raise KeyError(f"Provider '{preferred}' is not configured")
        return [self._config.primary, *self._config.fallbacks]

    def _select_provider(self, provider: Optional[str]) -> ProviderConfig:
        return self._provider_sequence(provider)[0]

    async def _get_or_create_client(self, provider_config: ProviderConfig) -> LLMClient:
        async with self._lock:
            if provider_config.name not in self._clients:
                self._clients[provider_config.name] = self._create_client(provider_config)
            return self._clients[provider_config.name]
    def _create_client(self, provider_config: ProviderConfig) -> LLMClient:
        name = provider_config.name.lower()

        if name in {"openrouter", "lmstudio", "lm_proxy", "openai-compatible"}:
            base_url = self._resolve_base_url(provider_config)
            api_key = provider_config.api_key or self._resolve_api_key(name)
            extra_headers = dict(provider_config.extra_headers)

            if name == "openrouter":
                referer = os.getenv("OPENROUTER_HTTP_REFERER")
                title = os.getenv("OPENROUTER_X_TITLE")
                if referer and "HTTP-Referer" not in extra_headers:
                    extra_headers["HTTP-Referer"] = referer
                if title and "X-Title" not in extra_headers:
                    extra_headers["X-Title"] = title

            return OpenAICompatibleClient(
                api_key=api_key,
                model=provider_config.model,
                base_url=base_url,
                timeout=provider_config.timeout,
                max_retries=provider_config.max_retries,
                provider_label=provider_config.provider_label or name,
                api_key_header=provider_config.api_key_header,
                extra_headers=extra_headers,
            )

        raise NotImplementedError(f"Provider '{provider_config.name}' is not supported yet.")

    def _resolve_base_url(self, provider_config: ProviderConfig) -> str:
        if provider_config.base_url:
            return provider_config.base_url

        name = provider_config.name.lower()
        if name == "openrouter":
            return os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if name == "lmstudio":
            return os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        if name == "lm_proxy":
            return os.getenv("LM_PROXY_BASE_URL", _DEFAULT_LM_PROXY_BASE_URL)
        return os.getenv("SCRAI_LLM_BASE_URL", "https://openrouter.ai/api/v1")

    def _resolve_api_key(self, name: str) -> Optional[str]:
        if name == "openrouter":
            return os.getenv("OPENROUTER_API_KEY")
        if name == "lmstudio":
            return os.getenv("LM_STUDIO_API_KEY")
        if name == "lm_proxy":
            return os.getenv("LM_PROXY_API_KEY")
        return os.getenv("SCRAI_LLM_API_KEY")
