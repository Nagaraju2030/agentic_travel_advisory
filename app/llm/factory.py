from app.core.config import settings
from app.llm.base import BaseLLM
from app.llm.mock import MockLLM


def build_llm() -> BaseLLM:
    if settings.llm_provider == "openai":
        from app.llm.openai_provider import OpenAILLM
        return OpenAILLM()
    return MockLLM()
