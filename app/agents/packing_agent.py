from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class PackingAgent(BaseAgent):
    name = "packing_agent"
    purpose = "Generates a weather- and trip-aware packing checklist."

    async def analyze(self, state: TravelState):
        weather = state.get_data("weather_agent").get("summary", {})
        avg_high = weather.get("average_high_c")
        rain = weather.get("max_rain_probability_pct")
        clothing = ["comfortable walking footwear", "mix-and-match travel clothing", "light layer for temperature changes"]
        if avg_high is not None and avg_high >= 30:
            clothing += ["breathable clothing", "sun hat"]
        if avg_high is not None and avg_high <= 12:
            clothing += ["warm insulating layer", "weather-appropriate outer layer"]
        if rain is not None and rain >= 50:
            clothing += ["compact rain protection", "water-resistant footwear option"]
        data = {
            "documents": ["passport/ID", "visa/entry approval if required", "insurance details", "transport/lodging confirmations", "offline document copies"],
            "clothing": clothing,
            "tech": ["phone", "charger", "power bank", "appropriate plug adapter", "offline maps/downloads"],
            "health": ["regular medicines", "basic personal-care items", "sun/heat or rain protection as conditions require"],
            "security": ["backup payment method stored separately", "small luggage lock if useful", "emergency contact card"],
        }
        warnings = [] if weather.get("forecast_available") else ["Packing list is generic because a live forecast was not available."]
        return data, warnings, [], 0.85
