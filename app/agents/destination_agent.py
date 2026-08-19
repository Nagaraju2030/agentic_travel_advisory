from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class DestinationResearchAgent(BaseAgent):
    name = "destination_research_agent"
    purpose = "Builds destination context such as country, language, currency and timezone."

    async def analyze(self, state: TravelState):
        profile, evidence = await self.tools.country_profile(state.request.destination)
        warnings = []
        if not profile.get("country"):
            warnings.append("Live destination metadata was unavailable; location-specific facts require verification.")
        data = {
            "destination": state.request.destination,
            "country_profile": profile,
            "planning_notes": [
                "Prefer neighborhoods with reliable public transport and late-arrival access.",
                "Keep offline copies of lodging address and essential travel documents.",
                "Confirm local payment acceptance and keep a backup payment method.",
            ],
        }
        return data, warnings, evidence, 0.9 if profile.get("country") else 0.65
