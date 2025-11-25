from .plugins.openai_llm import OpenAiLLM
from .config import LLMConfig
from providers.io_provider import IOProvider

def load_llm(llm_type: str, config: LLMConfig):
    """
    Factory that matches OM1 runtime signature.
    """
    if llm_type == "OpenAiLLM":
        return OpenAiLLM(
            config=config,
            io_provider=IOProvider()
        )

    raise ValueError(f"Unknown LLM type: {llm_type}")
