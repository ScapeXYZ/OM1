from pydantic import BaseModel
from typing import Optional

class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.1
    agent_name: str = "Assistant"  # <-- REQUIRED for LLMHistoryManager
