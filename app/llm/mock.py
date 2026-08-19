from __future__ import annotations

from app.llm.base import BaseLLM


class MockLLM(BaseLLM):
    async def generate(self, *, system: str, user: str) -> str:
        # Deliberately deterministic: the application remains fully runnable without a paid API.
        focus = user.replace("\n", " ")[:280]
        return (
            "Mock-mode AI note: review the structured evidence and recommendations produced by the specialist agents. "
            f"Request context: {focus}"
        )
