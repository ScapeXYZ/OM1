from typing import Generic, TypeVar, List, Dict, Optional
from pydantic import BaseModel

# Define output type for responses
R = TypeVar("R", bound=BaseModel)

class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.1
    agent_name: str = "Assistant"  # Added for LLMHistoryManager

class LLM(Generic[R]):
    """
    Base class for all LLM implementations.
    """
    def __init__(self, output_model: type[R], config: LLMConfig = LLMConfig()):
        self._output_model = output_model
        self._config = config

    async def ask(self, prompt: str, messages: List[Dict[str, str]] = []) -> Optional[R]:
        raise NotImplementedError("ask() not implemented in base LLM class")
