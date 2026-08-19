from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class TransportAgent(BaseAgent):
    name = "transport_agent"
    purpose = "Designs transport strategy and booking/connection safeguards."

    async def analyze(self, state: TravelState):
        r = state.request
        data = {
            "origin": r.origin,
            "destination": r.destination,
            "strategy": [
                "Compare total journey time, baggage rules, change fees, and connection risk—not only headline fare.",
                "Avoid overly tight self-transfer connections unless baggage and immigration timing are well understood.",
                "Pre-plan airport/station to lodging transfer for late arrival.",
                "Use official transit apps/sites to re-check service disruptions near travel time.",
            ],
            "local_mobility": [
                "Prioritize public transport for dense urban sightseeing where practical.",
                "Keep a licensed taxi/ride-hail backup for late-night or luggage-heavy movements.",
                "Validate accessibility against listed mobility needs before booking.",
            ],
            "mobility_needs": r.mobility_needs,
        }
        warnings = ["No live airline/rail inventory is queried in this starter; schedules and prices must be re-checked before booking."]
        return data, warnings, [], 0.8
