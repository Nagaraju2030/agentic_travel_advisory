from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agents.registry import AGENT_CATALOG
from app.models.schemas import AdvisoryResponse, TripRequest
from app.orchestration.workflow import TravelAdvisoryWorkflow

router = APIRouter(prefix="/v1")


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "agentic-travel-advisory"}


@router.get("/agents")
async def agents() -> dict:
    return {"count": len(AGENT_CATALOG), "agents": AGENT_CATALOG}


@router.post("/advisory", response_model=AdvisoryResponse)
async def create_advisory(request: TripRequest) -> AdvisoryResponse:
    return await TravelAdvisoryWorkflow().run(request)


@router.post("/advisory/stream")
async def stream_advisory(request: TripRequest) -> StreamingResponse:
    workflow = TravelAdvisoryWorkflow()

    async def event_generator():
        async for event in workflow.run_stream(request):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
