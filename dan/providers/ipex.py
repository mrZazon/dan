from __future__ import annotations

import logging
from typing import Any

from dan.providers.base import Provider, ProviderMessage, ProviderResponse

logger = logging.getLogger(__name__)


class IPEXProvider(Provider):
    """Intel IPEX-LLM provider - PRIMARY for D.A.N.

    Uses Intel IPEX-LLM for optimized inference on Intel hardware.
    Falls back gracefully if IPEX-LLM is not installed.

    Model loading uses ipex_llm.transformers.AutoModelForCausalLM
    and standard transformers.AutoTokenizer.
    """

    name = "ipex"

    def __init__(
        self, device: str = "cpu", quantization: str = "nf4", max_length: int = 2048,
    ) -> None:
        self._device = device
        self._quantization = quantization
        self._max_length = max_length
        self._model: Any = None
        self._tokenizer: Any = None
        self._model_name = ""
        self._available = False

    async def load_model(self, model_name: str) -> None:
        """Load a model using IPEX-LLM."""
        try:
            from ipex_llm.transformers import AutoModelForCausalLM
            from transformers import AutoTokenizer
        except ImportError:
            logger.error(
                "IPEX-LLM or transformers not installed. "
                "Install with: pip install ipex-llm transformers",
            )
            self._available = False
            return

        logger.info(
            "Loading model %s on %s (quant=%s)",
            model_name, self._device, self._quantization,
        )
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                model_name, trust_remote_code=True,
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                model_name,
                load_in_low_bit=self._quantization,
                device=self._device,
                trust_remote_code=True,
            )
            self._model_name = model_name
            self._available = True
            logger.info("Model %s loaded successfully", model_name)
        except Exception:
            logger.exception("Failed to load model %s", model_name)
            self._available = False

    async def unload_model(self) -> None:
        """Unload the current model from memory."""
        if self._model is not None:
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._model_name = ""
            self._available = False
            logger.info("Model unloaded")

    def is_loaded(self) -> bool:
        return self._available and self._model is not None

    async def health_check(self) -> bool:
        """Check if IPEX-LLM is available and a model is loaded."""
        if not self._available:
            try:
                import ipex_llm  # noqa: F401
                self._available = True
            except ImportError:
                return False
        return self.is_loaded()

    async def complete(
        self,
        messages: list[ProviderMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion using IPEX-LLM."""
        if not self.is_loaded():
            raise RuntimeError("No model loaded. Call load_model() first.")

        prompt = self._format_prompt(messages)
        try:
            input_ids = self._tokenizer(prompt, return_tensors="pt").input_ids
            output = self._model.generate(
                input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
            )
            generated = output[0][input_ids.shape[1]:]
            text = self._tokenizer.decode(generated, skip_special_tokens=True)
            return ProviderResponse(
                text=text,
                model=self._model_name,
                usage={
                    "prompt_tokens": int(input_ids.shape[1]),
                    "completion_tokens": len(generated),
                },
            )
        except Exception:
            logger.exception("IPEX-LLM completion failed")
            raise

    def _format_prompt(self, messages: list[ProviderMessage]) -> str:
        """Format messages into a ChatML prompt string."""
        bos = '<|im_start|>'
        eos = '<|im_end|>'
        parts: list[str] = []
        for msg in messages:
            parts.append(bos + msg.role)
            parts.append(msg.content)
            parts.append(eos)
        parts.append(bos + 'assistant')
        return chr(10).join(parts)
