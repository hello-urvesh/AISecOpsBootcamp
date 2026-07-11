"""Thin, robust wrapper around the `ollama` Python client.

Goals:
  * Surface clear, actionable errors for the two failures students will hit
    constantly: Ollama not running, and a requested model not pulled.
  * Stream tokens for a responsive UI.
  * Stay tolerant of both old (dict) and new (pydantic) response shapes
    from the ollama-python library across versions.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterator

from ollama import Client, ResponseError

from core.config import (
    DEFAULT_NUM_CTX,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    OLLAMA_HOST,
    PREFERRED_MODELS,
    REQUEST_TIMEOUT,
)

log = logging.getLogger(__name__)


class OllamaConnectionError(RuntimeError):
    """Raised when the Ollama daemon is unreachable."""


class OllamaModelError(RuntimeError):
    """Raised when a requested model is not available locally."""


@dataclass
class GenerationParams:
    """Sampling parameters surfaced to the UI."""
    temperature: float = DEFAULT_TEMPERATURE
    top_p: float = DEFAULT_TOP_P
    num_ctx: int = DEFAULT_NUM_CTX
    seed: int | None = None

    def to_options(self) -> dict[str, Any]:
        opts: dict[str, Any] = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "num_ctx": self.num_ctx,
        }
        if self.seed is not None:
            opts["seed"] = self.seed
        return opts


def _extract_chunk_content(chunk: Any) -> str:
    """Pull the assistant text out of a streaming chunk.

    ollama-python returns dicts in older versions and pydantic models in
    newer ones. Handle both without forcing a hard version pin.
    """
    # Newer pydantic-style: chunk.message.content
    msg = getattr(chunk, "message", None)
    if msg is not None:
        content = getattr(msg, "content", None)
        if content:
            return content
    # Older dict-style: chunk["message"]["content"]
    if isinstance(chunk, dict):
        msg_dict = chunk.get("message") or {}
        if isinstance(msg_dict, dict):
            return msg_dict.get("content") or ""
    return ""


def _extract_model_tag(item: Any) -> str | None:
    """Pull a model tag from a list() entry across library versions."""
    for attr in ("model", "name"):
        val = getattr(item, attr, None)
        if val:
            return val
    if isinstance(item, dict):
        return item.get("model") or item.get("name")
    return None


class OllamaService:
    """Stateless service: one instance per Streamlit session, cached as a resource."""

    def __init__(self, host: str = OLLAMA_HOST, timeout: float = REQUEST_TIMEOUT) -> None:
        self.host = host
        self.timeout = timeout
        try:
            self.client = Client(host=host, timeout=timeout)
        except Exception as e:  # construction shouldn't usually fail, but be safe
            raise OllamaConnectionError(
                f"Failed to construct Ollama client for {host}: {e}"
            ) from e

    # -- Model discovery --------------------------------------------------
    def list_models(self) -> list[str]:
        """Return tags installed locally; PREFERRED_MODELS bubble to the top."""
        try:
            response = self.client.list()
        except (ConnectionError, OSError) as e:
            raise OllamaConnectionError(
                f"Cannot reach Ollama at {self.host}. Is `ollama serve` running?"
            ) from e
        except Exception as e:
            raise OllamaConnectionError(
                f"Ollama list() failed against {self.host}: {e}"
            ) from e

        # Both pydantic ListResponse and old dict responses expose `.models` / ['models']
        raw_models = getattr(response, "models", None)
        if raw_models is None and isinstance(response, dict):
            raw_models = response.get("models", [])
        raw_models = raw_models or []

        installed: list[str] = []
        for item in raw_models:
            tag = _extract_model_tag(item)
            if tag:
                installed.append(tag)

        # Order: preferred first (in PREFERRED_MODELS order), then alphabetical remainder
        ordered: list[str] = [m for m in PREFERRED_MODELS if m in installed]
        for tag in sorted(installed):
            if tag not in ordered:
                ordered.append(tag)
        return ordered

    # -- Streaming chat ---------------------------------------------------
    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
        params: GenerationParams | None = None,
    ) -> Iterator[str]:
        """Yield response text chunks. Raises typed errors on failure."""
        params = params or GenerationParams()
        try:
            stream = self.client.chat(
                model=model,
                messages=messages,
                stream=True,
                options=params.to_options(),
            )
            for chunk in stream:
                content = _extract_chunk_content(chunk)
                if content:
                    yield content
        except (ConnectionError, OSError) as e:
            raise OllamaConnectionError(
                f"Lost connection to Ollama at {self.host}: {e}"
            ) from e
        except ResponseError as e:
            msg = (str(e) or "").lower()
            if "not found" in msg or "pull" in msg or "no such" in msg:
                raise OllamaModelError(
                    f"Model '{model}' is not available locally. "
                    f"Pull it with: `ollama pull {model}`"
                ) from e
            raise OllamaConnectionError(f"Ollama responded with an error: {e}") from e
        except Exception as e:
            log.exception("Unexpected error during Ollama chat_stream")
            raise OllamaConnectionError(f"Unexpected Ollama error: {e}") from e
