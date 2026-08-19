from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class LocalEtiquetteAgent(BaseAgent):
    name = "local_etiquette_agent"
    purpose = "Prepares culture, communication and responsible-tourism considerations."

    async def analyze(self, state: TravelState):
        country = state.get_data("destination_research_agent").get("country_profile", {})
        data = {
            "languages": country.get("languages", []),
            "recommendations": [
                "Learn basic greetings, thank-you, and emergency phrases in a commonly used local language.",
                "Follow posted rules for religious, heritage, photography, dress, and queueing contexts.",
                "Ask before photographing people and avoid disruptive behavior in residential areas.",
                "Prefer locally responsible operators and respect environmental restrictions.",
            ],
        }
        warnings = [] if country.get("languages") else ["Language metadata unavailable; verify local communication needs."]
        return data, warnings, [], 0.76
