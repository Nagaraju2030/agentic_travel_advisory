from datetime import date

import pytest

from app.llm.mock import MockLLM
from app.models.schemas import Evidence, TripRequest
from app.orchestration.workflow import TravelAdvisoryWorkflow
from app.tools.travel_data import TravelDataTools


class FakeTools(TravelDataTools):
    async def country_profile(self, destination: str):
        return (
            {
                "country": "Japan",
                "capital": "Tokyo",
                "currencies": ["JPY"],
                "languages": ["Japanese"],
                "geocoding": {"timezone": "Asia/Tokyo"},
            },
            [Evidence(source="test", detail="fake country profile")],
        )

    async def weather(self, request: TripRequest):
        return (
            {
                "available": True,
                "timezone": "Asia/Tokyo",
                "days": [
                    {
                        "date": "2026-09-15",
                        "temp_max_c": 27.0,
                        "temp_min_c": 20.0,
                        "precipitation_probability_pct": 30,
                        "weather_code": 1,
                    },
                    {
                        "date": "2026-09-16",
                        "temp_max_c": 26.0,
                        "temp_min_c": 19.0,
                        "precipitation_probability_pct": 70,
                        "weather_code": 61,
                    },
                ],
            },
            [Evidence(source="test", detail="fake weather")],
        )


@pytest.mark.asyncio
async def test_full_workflow_runs_all_agents():
    req = TripRequest(
        origin="Hyderabad, India",
        destination="Tokyo, Japan",
        start_date=date(2026, 9, 15),
        end_date=date(2026, 9, 16),
        travelers=2,
        budget=2000,
        interests=["food", "technology"],
    )
    workflow = TravelAdvisoryWorkflow(llm=MockLLM(), tools=FakeTools())
    result = await workflow.run(req)

    assert len(result.agents) == 13
    assert "final_advisory_agent" in result.agents
    assert len(result.advisory["day_by_day_itinerary"]) == 2
    assert result.advisory["budget"]["budget_supplied"] is True
