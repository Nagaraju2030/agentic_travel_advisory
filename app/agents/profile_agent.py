from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class ProfileAgent(BaseAgent):
    name = "profile_agent"
    purpose = "Normalizes traveler goals, constraints, trip duration and risk posture."

    async def analyze(self, state: TravelState):
        r = state.request
        data = {
            "trip_days": r.trip_days,
            "traveler_count": r.travelers,
            "budget_total": r.budget,
            "budget_per_person": round(r.budget / r.travelers, 2) if r.budget else None,
            "budget_per_person_per_day": round(r.budget / r.travelers / r.trip_days, 2) if r.budget else None,
            "interests": r.interests or ["general sightseeing"],
            "dietary_preferences": r.dietary_preferences,
            "mobility_needs": r.mobility_needs,
            "risk_tolerance": r.risk_tolerance,
            "planning_priorities": [
                "entry readiness",
                "safety and health checks",
                "weather-aware itinerary",
                "budget control",
                "transport feasibility",
            ],
        }
        warnings = [] if r.notes else ["No additional traveler notes were supplied; recommendations use the structured request only."]
        return data, warnings, [], 0.95
