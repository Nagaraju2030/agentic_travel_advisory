from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from app.agents.registry import AGENT_CLASSES
from app.core.config import settings
from app.llm.base import BaseLLM
from app.llm.factory import build_llm
from app.models.schemas import AdvisoryResponse, AgentResult, TripRequest, WorkflowEvent
from app.models.state import TravelState
from app.tools.travel_data import TravelDataTools


class TravelAdvisoryWorkflow:
    """Dependency-aware multi-agent workflow.

    Stages:
      1. Normalize traveler profile.
      2. Run independent destination intelligence agents in parallel.
      3. Run planning/economics agents that can consume stage 2.
      4. Build itinerary and packing plan from upstream results.
      5. Final lead-agent synthesis.
    """

    STAGES = [
        ["profile_agent"],
        [
            "destination_research_agent",
            "weather_agent",
            "safety_agent",
            "visa_entry_agent",
            "health_agent",
        ],
        ["local_etiquette_agent", "transport_agent", "accommodation_agent", "budget_agent"],
        ["itinerary_agent"],
        ["packing_agent"],
        ["final_advisory_agent"],
    ]

    def __init__(self, llm: BaseLLM | None = None, tools: TravelDataTools | None = None) -> None:
        self.llm = llm or build_llm()
        self.tools = tools or TravelDataTools()
        self.agents = {cls.name: cls(self.llm, self.tools) for cls in AGENT_CLASSES}
        self.semaphore = asyncio.Semaphore(settings.max_parallel_agents)

    async def _run_agent(self, name: str, state: TravelState) -> AgentResult:
        async with self.semaphore:
            state.workflow.append(WorkflowEvent(stage="agent", agent=name, status="started"))
            result = await self.agents[name].execute(state)
            state.put(result)
            state.workflow.append(WorkflowEvent(stage="agent", agent=name, status=result.status))
            return result

    async def run(self, request: TripRequest) -> AdvisoryResponse:
        state = TravelState(request=request)
        for index, stage in enumerate(self.STAGES, start=1):
            state.workflow.append(WorkflowEvent(stage=f"stage_{index}", status="started"))
            await asyncio.gather(*(self._run_agent(name, state) for name in stage))
            state.workflow.append(WorkflowEvent(stage=f"stage_{index}", status="completed"))

        advisory = state.get_data("final_advisory_agent")
        return AdvisoryResponse(
            request=request,
            advisory=advisory,
            agents=state.results,
            workflow=state.workflow,
        )

    async def run_stream(self, request: TripRequest) -> AsyncGenerator[dict, None]:
        state = TravelState(request=request)
        yield {"type": "workflow_started", "agents": sum(len(x) for x in self.STAGES)}

        for index, stage in enumerate(self.STAGES, start=1):
            yield {"type": "stage_started", "stage": index, "agents": stage}
            results = await asyncio.gather(*(self._run_agent(name, state) for name in stage))
            for result in results:
                yield {
                    "type": "agent_completed",
                    "stage": index,
                    "agent": result.agent,
                    "status": result.status,
                    "confidence": result.confidence,
                    "duration_ms": result.duration_ms,
                }
            yield {"type": "stage_completed", "stage": index}

        response = AdvisoryResponse(
            request=request,
            advisory=state.get_data("final_advisory_agent"),
            agents=state.results,
            workflow=state.workflow,
        )
        yield {"type": "workflow_completed", "result": response.model_dump(mode="json")}
