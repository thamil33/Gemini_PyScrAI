"""Abstract base client and models for LLM integrations."""

from __future__ import annotations

import abc
import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional


@dataclass(slots=True)
class LLMUsage:
    """Token usage metadata returned by providers."""

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class LLMMessage:
    """Chat message exchanged with an LLM."""

    role: str
    content: str


@dataclass(slots=True)
class LLMResponse:
    """Standardized LLM response payload."""

    content: str
    model: str
    provider: str
    usage: Optional[LLMUsage] = None
    finish_reason: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class LLMClientError(RuntimeError):
    """Base error class for LLM clients."""

    def __init__(self, message: str, *, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model


class LLMRateLimitError(LLMClientError):
    """Raised when a provider rejects a request due to rate limiting."""


class LLMClient(abc.ABC):
    """Abstract interface for language model providers."""

    def __init__(self, *, provider: str, model: str):
        self._provider = provider
        self._model = model

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    @abc.abstractmethod
    async def generate_response(
        self,
        messages: Iterable[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response from the provider."""

    @abc.abstractmethod
    async def validate_connection(self) -> bool:
        """Validate connectivity and credentials for the provider."""

    @abc.abstractmethod
    async def list_models(self) -> List[str]:
        """Return models available for this provider/account."""

    async def close(self) -> None:
        """Override to release any client resources (optional)."""
        return None


def ensure_messages(payload: Iterable[Mapping[str, str] | LLMMessage]) -> List[LLMMessage]:
    """Convert dictionaries into `LLMMessage` instances if needed."""

    normalized: List[LLMMessage] = []
    for item in payload:
        if isinstance(item, LLMMessage):
            normalized.append(item)
        else:
            role = item.get("role")
            content = item.get("content")
            if role is None or content is None:
                raise ValueError("Messages must include 'role' and 'content'.")
            normalized.append(LLMMessage(role=role, content=content))
    return normalized
