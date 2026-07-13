from __future__ import annotations

import re
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from dan.providers.base import Provider, ProviderMessage, ProviderResponse

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaProvider(Provider):
    """Ollama provider for D.A.N.

    Uses a running Ollama server for local LLM inference.
    Requires Ollama to be installed and running (https://ollama.com).
    """

    name = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._model_name = ""
        self._available = False

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def load_model(self, model_name: str) -> None:
        """Verify the model exists in Ollama, pulling if necessary."""
        logger.info("Checking Ollama model: %s", model_name)
        try:
            async with self._client() as client:
                resp = await client.post("/api/pull", json={"name": model_name})
                resp.raise_for_status()
                self._model_name = model_name
                self._available = True
                logger.info("Model %s ready in Ollama", model_name)
        except httpx.HTTPError:
            logger.exception("Failed to pull model %s from Ollama", model_name)
            self._available = False

    async def unload_model(self) -> None:
        """Release reference to the current model."""
        self._model_name = ""
        self._available = False
        logger.info("Model reference released")

    def is_loaded(self) -> bool:
        return self._available and bool(self._model_name)

    @staticmethod
    def _strip_thinking(text: str) -> str:
        """Remove <think>...</think> tags and any leading/trailing whitespace."""
        return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()

    async def health_check(self) -> bool:
        """Check if the Ollama server is reachable."""
        try:
            async with self._client() as client:
                resp = await client.get("/api/tags")
                resp.raise_for_status()
                return True
        except httpx.HTTPError:
            return False

    async def complete(
        self,
        messages: list[ProviderMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion via Ollama's chat API."""
        if not self.is_loaded():
            raise RuntimeError("No model loaded. Call load_model() first.")

        payload: dict[str, Any] = {
            "model": self._model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "think": False,
            },
        }

        try:
            async with self._client() as client:
                resp = await client.post("/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()

            text = data.get("message", {}).get("content", "")
            text = self._strip_thinking(text)
            usage = {}
            if "prompt_eval_count" in data:
                usage["prompt_tokens"] = data["prompt_eval_count"]
            if "eval_count" in data:
                usage["completion_tokens"] = data["eval_count"]

            return ProviderResponse(
                text=text,
                model=self._model_name,
                usage=usage,
            )
        except httpx.HTTPError:
            logger.exception("Ollama completion failed")
            raise

    async def stream(
        self,
        messages: list[ProviderMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a completion token by token via Ollama's streaming API."""
        if not self.is_loaded():
            raise RuntimeError("No model loaded. Call load_model() first.")

        payload: dict[str, Any] = {
            "model": self._model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "think": False,
            },
        }

        import json as _json

        thinking = False
        async with self._client() as client:
            async with client.stream("POST", "/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    chunk = _json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if not content:
                        continue
                    if "<think>" in content:
                        thinking = True
                    if thinking:
                        if "</think>" in content:
                            thinking = False
                            after = content.split("</think>", 1)[1]
                            if after:
                                yield after
                        continue
                    yield content
