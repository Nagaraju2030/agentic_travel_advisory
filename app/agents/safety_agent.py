from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class SafetyAgent(BaseAgent):
    name = "safety_agent"
    purpose = "Produces a risk-control checklist without fabricating live government advisories."

    async def analyze(self, state: TravelState):
        r = state.request
        risk_actions = {
            "low": ["Avoid isolated areas at night", "Use licensed transport", "Share itinerary with a trusted contact"],
            "medium": ["Use licensed transport", "Keep document backups", "Use hotel safe for spare cards/cash"],
            "high": ["Still respect official warnings", "Avoid unnecessary exposure to known high-risk areas", "Maintain emergency contacts"],
        }
        data = {
            "risk_tolerance": r.risk_tolerance,
            "controls": risk_actions[r.risk_tolerance],
            "emergency_readiness": [
                "Save local emergency numbers after arrival.",
                "Store passport/insurance copies separately from originals.",
                "Enable device lock, remote wipe, and secure public-Wi-Fi practices.",
            ],
            "official_verification": self.tools.authoritative_verification_tasks(r.destination)[1],
        }
        warnings = ["This agent does not claim a live government risk rating; verify the current official travel advisory before departure."]
        return data, warnings, [], 0.82
