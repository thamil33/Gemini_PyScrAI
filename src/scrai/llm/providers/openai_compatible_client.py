"""Generic OpenAI-compatible provider implementation for ScrAI."""

from __future__ import annotations

import asyncio
import dataclasses
import logging
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests

from ..base import (
    LLMClient,
    LLMClientError,
    LLMMessage,
    LLMRateLimitError,
    LLMResponse,
    LLMUsage,
    ensure_messages,
)

logger = logging.getLogger(__name__)


DEFAULT_OPENROUTER_MODEL = "openrouter/gpt-4.1-mini"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_LM_STUDIO_BASE_URL = "http://localhost:1234/v1"


class OpenAICompatibleClient(LLMClient):
    """Async-friendly wrapper around any OpenAI-compatible HTTP API."""

    CHAT_COMPLETIONS_ENDPOINT = "/chat/completions"
    MODELS_ENDPOINT = "/models"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        provider_label: str = "openrouter",
        api_key_header: str = "Authorization",
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        resolved_base_url = base_url or DEFAULT_OPENROUTER_BASE_URL
        resolved_model = model or DEFAULT_OPENROUTER_MODEL

        # For local LM Studio or LM Proxy, API key may be optional.
        api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("LM_PROXY_API_KEY")
        if "http://localhost" not in resolved_base_url and "https://localhost" not in resolved_base_url:
            if not api_key:
                raise ValueError(
                    "API key must be provided via argument or environment variable for remote providers."
                )

        super().__init__(provider=provider_label, model=resolved_model)
        self._api_key = api_key
        self._base_url = resolved_base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._api_key_header = api_key_header
        self._extra_headers = dict(extra_headers or {})
        self._session = requests.Session()

    async def generate_response(
        self,
        messages: Iterable[LLMMessage | Mapping[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat completion using an OpenAI-compatible API."""

        normalized = ensure_messages(messages)
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [dataclasses.asdict(msg) for msg in normalized],
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if response_format is not None:
            payload["response_format"] = response_format

        payload.update(kwargs)

        response_data = await self._request("POST", self.CHAT_COMPLETIONS_ENDPOINT, json=payload)

        try:
            choice = response_data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:  # pragma: no cover - defensive
            raise LLMClientError(
                f"Unexpected response format received from provider '{self.provider}': {response_data}",
                provider=self.provider,
                model=self.model,
            ) from exc

        usage_meta = response_data.get("usage")
        usage = (
            LLMUsage(
                prompt_tokens=usage_meta.get("prompt_tokens"),
                completion_tokens=usage_meta.get("completion_tokens"),
                total_tokens=usage_meta.get("total_tokens"),
                raw=usage_meta,
            )
            if usage_meta
            else None
        )

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider,
            finish_reason=finish_reason,
            usage=usage,
            raw=response_data,
        )

    async def validate_connection(self) -> bool:
        try:
            await self.list_models()
            return True
        except LLMClientError as exc:
            logger.warning("LLM validation failed for provider '%s': %s", self.provider, exc)
            return False

    async def list_models(self) -> List[str]:
        response_data = await self._request("GET", self.MODELS_ENDPOINT)
        models = [item["id"] for item in response_data.get("data", [])]
        return models

    async def close(self) -> None:
        self._session.close()

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute an HTTP request in an async-friendly manner with retries."""

        url = f"{self._base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            **self._extra_headers,
        }
        if self._api_key:
            headers[self._api_key_header] = f"Bearer {self._api_key}" if self._api_key_header.lower() == "authorization" else self._api_key

        loop = asyncio.get_running_loop()

        for attempt in range(1, self._max_retries + 1):
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda: self._session.request(
                        method,
                        url,
                        headers=headers,
                        timeout=self._timeout,
                        **kwargs,
                    ),
                )

                if response.status_code == 429:
                    raise LLMRateLimitError(
                        f"{self.provider} rate limit exceeded",
                        provider=self.provider,
                        model=self.model,
                    )

                if response.status_code >= 400:
                    raise LLMClientError(
                        f"{self.provider} request failed with status {response.status_code}: {response.text}",
                        provider=self.provider,
                        model=self.model,
                    )

                return response.json()

            except (LLMClientError, LLMRateLimitError):
                raise
            except Exception as exc:  # pragma: no cover - network errors
                logger.warning(
                    "%s request attempt %s failed: %s", self.provider, attempt, exc, exc_info=exc
                )
                if attempt == self._max_retries:
                    raise LLMClientError(
                        f"{self.provider} request failed after {self._max_retries} attempts: {exc}",
                        provider=self.provider,
                        model=self.model,
                    ) from exc

        raise LLMClientError("LLM request failed unexpectedly", provider=self.provider, model=self.model)
