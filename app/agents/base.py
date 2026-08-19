from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any

from app.llm.base import BaseLLM
from app.models.schemas import AgentResult
from app.models.state import TravelState
from app.tools.travel_data import TravelDataTools


class BaseAgent(ABC):
    name = "base"
    purpose = "Base travel agent"

    def __init__(self, llm: BaseLLM, tools: TravelDataTools) -> None:
        self.llm = llm
        self.tools = tools

    async def execute(self, state: TravelState) -> AgentResult:
        started = time.perf_counter()
        try:
            data, warnings, evidence, confidence = await self.analyze(state)
            if data and "ai_notes" not in data:
                try:
                    data["ai_notes"] = await self._ai_notes(state, data)
                except Exception as llm_exc:
                    data["ai_notes"] = "LLM enrichment unavailable; structured specialist output is preserved."
                    warnings.append(f"LLM enrichment failed safely: {type(llm_exc).__name__}")
            status = "partial" if warnings else "ok"
            result = AgentResult(
                agent=self.name,
                status=status,
                confidence=confidence,
                data=data,
                warnings=warnings,
                evidence=evidence,
            )
        except Exception as exc:
            result = AgentResult(
                agent=self.name,
                status="failed",
                confidence=0.0,
                data={},
                warnings=[f"{self.name} failed safely: {type(exc).__name__}: {exc}"],
            )
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        return result

    async def _ai_notes(self, state: TravelState, data: dict[str, Any]) -> str:
        system = (
            f"You are the {self.name} specialist inside a multi-agent travel advisory system. "
            "Use only the supplied trip context and structured findings. Do not invent live visa, safety, health, price, or schedule facts. "
            "Give a concise production-quality recommendation and explicitly flag anything that needs official verification."
        )
        user = json.dumps(
            {"trip": state.request.model_dump(mode="json"), "findings": data},
            ensure_ascii=False,
            default=str,
        )
        return await self.llm.generate(system=system, user=user)

    @abstractmethod
    async def analyze(self, state: TravelState) -> tuple[dict, list[str], list, float]:
        raise NotImplementedError
