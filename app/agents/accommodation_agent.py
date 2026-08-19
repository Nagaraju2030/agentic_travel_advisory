from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class AccommodationAgent(BaseAgent):
    name = "accommodation_agent"
    purpose = "Defines lodging selection criteria around safety, transport, budget and traveler needs."

    async def analyze(self, state: TravelState):
        r = state.request
        data = {
            "selection_scorecard": {
                "transit_access": 25,
                "area_suitability": 20,
                "recent_guest_feedback": 15,
                "cancellation_flexibility": 15,
                "total_price_with_fees": 15,
                "traveler_specific_needs": 10,
            },
            "requirements": [
                "Verify final price including taxes/fees.",
                "Prefer flexible cancellation until key travel documents are confirmed.",
                "Check late check-in policy against arrival time.",
                "Confirm room accessibility/bed setup directly when essential.",
            ],
            "mobility_needs": r.mobility_needs,
        }
        warnings = ["This project does not scrape or book hotels; integrate an approved inventory provider for live availability."]
        return data, warnings, [], 0.8
