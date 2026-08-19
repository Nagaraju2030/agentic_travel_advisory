from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class TripRequest(BaseModel):
    origin: str = Field(..., examples=["Hyderabad, India"])
    destination: str = Field(..., examples=["Tokyo, Japan"])
    start_date: date
    end_date: date
    travelers: int = Field(default=1, ge=1, le=20)
    passport_country: str | None = Field(default=None, description="Passport nationality/country used for entry-rule verification")
    residency_country: str | None = Field(default=None, description="Current country of residence, if relevant to travel planning")
    budget: float | None = Field(default=None, gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    interests: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    mobility_needs: list[str] = Field(default_factory=list)
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TripRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 60:
            raise ValueError("Trips longer than 60 days are not supported in this demo")
        return self

    @property
    def trip_days(self) -> int:
        return (self.end_date - self.start_date).days + 1


class Evidence(BaseModel):
    source: str
    detail: str
    url: str | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentResult(BaseModel):
    agent: str
    status: Literal["ok", "partial", "failed"] = "ok"
    confidence: float = Field(default=0.75, ge=0, le=1)
    data: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    duration_ms: int = 0


class WorkflowEvent(BaseModel):
    stage: str
    agent: str | None = None
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AdvisoryResponse(BaseModel):
    request: TripRequest
    advisory: dict[str, Any]
    agents: dict[str, AgentResult]
    workflow: list[WorkflowEvent]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    disclaimer: str = (
        "Travel rules, health guidance, safety conditions, prices, and transport schedules can change. "
        "Verify time-sensitive decisions with official government, airline, embassy/consulate, and local authority sources."
    )
