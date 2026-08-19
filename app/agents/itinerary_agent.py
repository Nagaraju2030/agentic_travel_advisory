from __future__ import annotations

from datetime import timedelta

from app.agents.base import BaseAgent
from app.models.state import TravelState


class ItineraryAgent(BaseAgent):
    name = "itinerary_agent"
    purpose = "Builds a balanced day-by-day plan using upstream weather, budget, safety and interests."

    async def analyze(self, state: TravelState):
        r = state.request
        interests = r.interests or ["city highlights", "local culture", "food"]
        weather_days = {d.get("date"): d for d in state.get_data("weather_agent").get("daily_forecast", [])}
        itinerary = []
        for idx in range(r.trip_days):
            day = r.start_date + timedelta(days=idx)
            interest = interests[idx % len(interests)]
            forecast = weather_days.get(day.isoformat(), {})
            rain = forecast.get("precipitation_probability_pct")
            indoor_bias = rain is not None and rain >= 60
            itinerary.append(
                {
                    "day": idx + 1,
                    "date": day.isoformat(),
                    "theme": interest,
                    "morning": "Indoor/covered priority activity" if indoor_bias else f"Primary {interest} activity",
                    "afternoon": "Flexible indoor experience + local meal" if indoor_bias else "Secondary nearby attraction + local meal",
                    "evening": "Low-friction neighborhood activity near lodging",
                    "weather_adjustment": f"Rain probability {rain}%" if rain is not None else "Refresh forecast closer to date",
                    "pace_rule": "Keep 20–30% of the day unscheduled for transit, rest, queues, and spontaneous changes.",
                }
            )
        data = {
            "days": itinerary,
            "routing_principle": "Cluster activities geographically to reduce backtracking and transport cost.",
            "booking_principle": "Pre-book only capacity-constrained/high-priority items; keep the rest flexible.",
        }
        warnings = []
        if not weather_days:
            warnings.append("Itinerary uses no live forecast because weather data was unavailable/outside forecast horizon.")
        return data, warnings, [], 0.86
