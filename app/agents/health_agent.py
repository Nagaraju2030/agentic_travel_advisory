from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState

class HealthAgent(BaseAgent):
    name = "health_agent"
    purpose = "Creates a conservative travel-health preparedness plan."

    async def analyze(self, state: TravelState):
        data = {
            "pre_departure": [
                "Review destination-specific public-health guidance from an official source.",
                "Confirm travel insurance includes medical treatment and evacuation where appropriate.",
                "Carry essential prescription medicines in original packaging with supporting documentation when required.",
            ],
            "during_trip": [
                "Maintain hydration and sun/heat protection appropriate to conditions.",
                "Use safe food/water practices where local guidance recommends them.",
                "Know how to reach urgent medical care near primary lodging.",
            ],
            "mobility_considerations": state.request.mobility_needs,
            "official_verification": self.tools.authoritative_verification_tasks(state.request.destination)[3],
        }
        warnings = ["This is travel-planning guidance, not medical advice; vaccination and medication decisions require appropriate professional/official guidance."]
        return data, warnings, [], 0.84
