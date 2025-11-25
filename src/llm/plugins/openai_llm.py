import time
import logging
from typing import List, Dict, Optional, Type
from pydantic import BaseModel

from ..base import LLM, LLMConfig
from providers.io_provider import IOProvider
from providers.llm_history_manager import LLMHistoryManager
from openai import AsyncOpenAI


class OpenAiLLM(LLM):
    """OpenAI-based LLM implementation for GPT models."""

    def __init__(self, config: LLMConfig, io_provider: Optional[IOProvider] = None):
        super().__init__(config, io_provider)
        self._config = config
        self.io_provider = io_provider

        if not config.api_key:
            raise ValueError("config file missing api_key")

        # Default model if none given
        if not config.model:
            self._config.model = "gpt-4o-mini"

        # Create OpenAI async client
        self._client = AsyncOpenAI(api_key=config.api_key)

        # History manager  (IMPORTANT: keyword args so OM1 receives correct objects)
        self.history_manager = LLMHistoryManager(
            config=self._config,
            io_provider=self.io_provider,
            client=self._client
        )

    async def ask(self, prompt: str, messages: List[Dict[str, str]] = []) -> Optional[str]:
        """Send prompt to OpenAI API and return string output."""
        try:
            logging.info(f"OpenAI LLM prompt: {prompt}")
            self.io_provider.llm_start_time = time.time()
            self.io_provider.set_llm_prompt(prompt)

            response = await self._client.chat.completions.create(
                model=self._config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._config.temperature,
            )

            message_content = response.choices[0].message.content
            self.io_provider.llm_end_time = time.time()
            logging.info(f"OpenAI LLM output: {message_content}")
            return message_content

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return None


__all__ = ["OpenAiLLM"]
