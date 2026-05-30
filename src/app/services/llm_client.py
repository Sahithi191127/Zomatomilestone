"""LLM client abstraction — Groq milestone provider."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base error for LLM provider failures."""


class LLMRateLimitError(LLMClientError):
    pass


class LLMTimeoutError(LLMClientError):
    pass


@dataclass
class CompletionOptions:
    temperature: float = 0.3
    max_tokens: int = 2048
    json_mode: bool = True


class LLMClient(ABC):
    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, str]],
        options: CompletionOptions | None = None,
    ) -> str:
        """Return raw text content from the model."""


class GroqClient(LLMClient):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._api_key = api_key or settings.llm_api_key
        self._model = model or settings.llm_model
        self._base_url = base_url or settings.groq_base_url
        if not self._api_key:
            raise LLMClientError("LLM_API_KEY is not set")

    def complete(
        self,
        messages: list[dict[str, str]],
        options: CompletionOptions | None = None,
    ) -> str:
        opts = options or CompletionOptions()
        try:
            from groq import Groq
        except ImportError as exc:
            raise LLMClientError("groq package is not installed") from exc

        # Groq SDK appends /openai/v1/... — use https://api.groq.com only (not .../openai/v1)
        client = Groq(api_key=self._api_key, base_url=self._base_url.rstrip("/"))
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": opts.temperature,
            "max_tokens": opts.max_tokens,
        }
        if opts.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                if not content or not str(content).strip():
                    raise LLMClientError("Empty response from Groq")
                return str(content).strip()
            except Exception as exc:
                last_error = exc
                err_str = str(exc).lower()
                if "429" in err_str or "rate" in err_str:
                    if attempt == 0:
                        time.sleep(1.5)
                        continue
                    raise LLMRateLimitError(str(exc)) from exc
                if "timeout" in err_str:
                    if attempt == 0:
                        time.sleep(1.0)
                        continue
                    raise LLMTimeoutError(str(exc)) from exc
                if attempt == 0:
                    time.sleep(1.0)
                    continue
                raise LLMClientError(str(exc)) from exc

        raise LLMClientError(str(last_error) if last_error else "Unknown Groq error")


def get_llm_client(provider: str | None = None) -> LLMClient:
    """Factory — milestone default is Groq."""
    name = (provider or settings.llm_provider).lower()
    if name == "groq":
        return GroqClient()
    raise LLMClientError(f"Unsupported LLM_PROVIDER: {name}")
