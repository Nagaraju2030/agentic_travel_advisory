from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class VisaEntryAgent(BaseAgent):
    name = "visa_entry_agent"
    purpose = "Builds an entry-document readiness checklist and routes legal facts to official verification."

    async def analyze(self, state: TravelState):
        r = state.request
        warnings = []
        if not r.passport_country:
            warnings.append("Passport country was not supplied; exact entry-rule verification cannot be personalized.")
        data = {
            "traveler_origin": r.origin,
            "passport_country": r.passport_country,
            "residency_country": r.residency_country,
            "destination": r.destination,
            "entry_readiness_checklist": [
                "Confirm visa/visa-waiver/eTA requirement for the traveler's passport nationality.",
                "Confirm passport minimum validity and blank-page requirements.",
                "Check onward/return ticket and proof-of-funds requirements.",
                "Check transit visa rules for every connection country.",
                "Confirm arrival forms, customs declarations, and any required pre-registration.",
            ],
            "official_verification": self.tools.authoritative_verification_tasks(r.destination)[0],
        }
        warnings.append("Immigration rules are legal and time-sensitive; this workflow intentionally does not invent a visa decision.")
        return data, warnings, [], 0.9 if r.passport_country else 0.78
