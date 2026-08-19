from __future__ import annotations

from dataclasses import dataclass, field

from app.models.schemas import AgentResult, TripRequest, WorkflowEvent


@dataclass
class TravelState:
    request: TripRequest
    results: dict[str, AgentResult] = field(default_factory=dict)
    workflow: list[WorkflowEvent] = field(default_factory=list)

    def put(self, result: AgentResult) -> None:
        self.results[result.agent] = result

    def get_data(self, agent_name: str) -> dict:
        result = self.results.get(agent_name)
        return result.data if result else {}
