from __future__ import annotations

from openai import AsyncOpenAI

from app.core.config import settings
from app.llm.base import BaseLLM


class OpenAILLM(BaseLLM):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout_seconds,
        )

    async def generate(self, *, system: str, user: str) -> str:
        response = await self.client.responses.create(
            model=settings.openai_model,
            instructions=system,
            input=user,
        )
        text = getattr(response, "output_text", None)
        if text:
            return text.strip()

        # Defensive fallback for SDK/model response-shape differences.
        chunks: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                value = getattr(content, "text", None)
                if value:
                    chunks.append(value)
        return "\n".join(chunks).strip() or "No LLM narrative was returned."
