from __future__ import annotations

from app.agents.base import BaseAgent
from app.models.state import TravelState


class BudgetAgent(BaseAgent):
    name = "budget_agent"
    purpose = "Allocates the requested budget and identifies cost-control guardrails."

    async def analyze(self, state: TravelState):
        r = state.request
        warnings = []
        if not r.budget:
            data = {
                "budget_supplied": False,
                "recommended_categories": ["transport", "lodging", "food", "activities", "local transit", "contingency"],
                "guardrails": ["Set a total cap before booking", "Reserve a contingency buffer", "Track non-refundable commitments separately"],
            }
            warnings.append("No total budget was supplied, so monetary allocation is not calculated.")
            return data, warnings, [], 0.72

        ratios = {
            "transport": 0.28,
            "lodging": 0.32,
            "food": 0.16,
            "activities": 0.10,
            "local_transit": 0.06,
            "contingency": 0.08,
        }
        allocation = {k: round(r.budget * v, 2) for k, v in ratios.items()}
        data = {
            "budget_supplied": True,
            "currency": r.currency.upper(),
            "total": r.budget,
            "per_person": round(r.budget / r.travelers, 2),
            "per_person_per_day": round(r.budget / r.travelers / r.trip_days, 2),
            "planning_allocation": allocation,
            "guardrails": [
                "Treat allocation as a planning envelope, not a live price quote.",
                "Protect contingency until transport and lodging are confirmed.",
                "Compare total landed cost, including baggage, taxes, resort/city fees, and payment FX fees.",
            ],
        }
        return data, warnings, [], 0.9
