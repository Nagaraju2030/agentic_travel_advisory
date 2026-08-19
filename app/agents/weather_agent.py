from __future__ import annotations

from statistics import mean

from app.agents.base import BaseAgent
from app.models.state import TravelState


class WeatherAgent(BaseAgent):
    name = "weather_agent"
    purpose = "Retrieves forecast data and translates it into travel-impact recommendations."

    async def analyze(self, state: TravelState):
        weather, evidence = await self.tools.weather(state.request)
        days = weather.get("days") or []
        warnings = []
        summary = {"forecast_available": bool(days)}
        if days:
            maxes = [d["temp_max_c"] for d in days if d.get("temp_max_c") is not None]
            mins = [d["temp_min_c"] for d in days if d.get("temp_min_c") is not None]
            rain = [d["precipitation_probability_pct"] for d in days if d.get("precipitation_probability_pct") is not None]
            summary.update(
                {
                    "average_high_c": round(mean(maxes), 1) if maxes else None,
                    "average_low_c": round(mean(mins), 1) if mins else None,
                    "max_rain_probability_pct": max(rain) if rain else None,
                }
            )
        else:
            warnings.append(weather.get("reason", "Weather forecast unavailable for these dates."))
            warnings.append("Use seasonal planning now and refresh the forecast closer to departure.")
        data = {"summary": summary, "daily_forecast": days, "timezone": weather.get("timezone")}
        return data, warnings, evidence, 0.95 if days else 0.55
