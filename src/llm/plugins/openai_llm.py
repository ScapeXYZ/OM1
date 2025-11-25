import time
import logging
from typing import List, Dict, Optional, Type
from pydantic import BaseModel

<<<<<<< HEAD
from ..base import LLM, LLMConfig
from providers.io_provider import IOProvider
=======
from llm import LLM, LLMConfig
from llm.function_schemas import convert_function_calls_to_actions
from llm.output_model import CortexOutputModel
from providers.avatar_llm_state_provider import AvatarLLMState
>>>>>>> upstream/main
from providers.llm_history_manager import LLMHistoryManager
from openai import AsyncOpenAI


<<<<<<< HEAD
class OpenAiLLM(LLM):
    """OpenAI-based LLM implementation for GPT models."""

    def __init__(self, config: LLMConfig, io_provider: Optional[IOProvider] = None):
        super().__init__(config, io_provider)
        self._config = config
        self.io_provider = io_provider
=======
class OpenAILLM(LLM[R]):
    """
    An OpenAI-based Language Learning Model implementation with function call support.

    This class implements the LLM interface for OpenAI's GPT models, handling
    configuration, authentication, and async API communication. It supports both
    traditional JSON structured output and function calling.

    Parameters
    ----------
    config : LLMConfig
        Configuration object containing API settings. If not provided, defaults
        will be used.
    available_actions : list[AgentAction], optional
        List of available actions for function call generation. If provided,
        the LLM will use function calls instead of structured JSON output.
    """

    def __init__(
        self,
        config: LLMConfig = LLMConfig(),
        available_actions: T.Optional[T.List] = None,
    ):
        """
        Initialize the OpenAI LLM instance.

        Parameters
        ----------
        config : LLMConfig, optional
            Configuration settings for the LLM.
        available_actions : list[AgentAction], optional
            List of available actions for function calling.
        """
        super().__init__(config, available_actions)
>>>>>>> upstream/main

        if not config.api_key:
            raise ValueError("config file missing api_key")

        # Default model if none given
        if not config.model:
            self._config.model = "gpt-4.1-mini"

        # Create OpenAI async client
        self._client = AsyncOpenAI(api_key=config.api_key)

        # History manager  (IMPORTANT: keyword args so OM1 receives correct objects)
        self.history_manager = LLMHistoryManager(
            config=self._config,
            io_provider=self.io_provider,
            client=self._client
        )

<<<<<<< HEAD
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
=======
        # Initialize history manager
        self.history_manager = LLMHistoryManager(self._config, self._client)

    @AvatarLLMState.trigger_thinking()
    @LLMHistoryManager.update_history()
    async def ask(
        self, prompt: str, messages: T.List[T.Dict[str, T.Any]] = []
    ) -> R | None:
        """
        Send a prompt to the OpenAI API and get a structured response.

        Parameters
        ----------
        prompt : str
            The input prompt to send to the model.
        messages : List[Dict[str, str]]
            List of message dictionaries to send to the model.

        Returns
        -------
        R or None
            Parsed response matching the output_model structure, or None if
            parsing fails.
        """
        try:
            logging.info(f"OpenAI LLM input: {prompt}")
            logging.debug(f"OpenAI LLM messages: {messages}")

            self.io_provider.llm_start_time = time.time()
            self.io_provider.set_llm_prompt(prompt)

            formatted_messages = [
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                for msg in messages
            ]
            formatted_messages.append({"role": "user", "content": prompt})

            response = await self._client.chat.completions.create(
                model=self._config.model or "gpt-5",
                messages=T.cast(T.Any, formatted_messages),
                tools=T.cast(T.Any, self.function_schemas),
                tool_choice="auto",
                timeout=self._config.timeout,
>>>>>>> upstream/main
            )

            message = response.choices[0].message
            self.io_provider.llm_end_time = time.time()
            logging.info(f"OpenAI LLM output: {message_content}")
            return message_content

<<<<<<< HEAD
=======
            if message.tool_calls:
                logging.info(f"Received {len(message.tool_calls)} function calls")
                logging.info(f"Function calls: {message.tool_calls}")

                function_call_data = [
                    {
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message.tool_calls
                ]

                actions = convert_function_calls_to_actions(function_call_data)

                result = CortexOutputModel(actions=actions)
                logging.info(f"OpenAI LLM function call output: {result}")
                return T.cast(R, result)

            return None

>>>>>>> upstream/main
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return None


__all__ = ["OpenAiLLM"]
