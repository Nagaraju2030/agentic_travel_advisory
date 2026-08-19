from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.models.schemas import TripRequest
from app.orchestration.workflow import TravelAdvisoryWorkflow


async def main() -> None:
    payload = json.loads((Path(__file__).parent / "request.json").read_text())
    request = TripRequest.model_validate(payload)
    result = await TravelAdvisoryWorkflow().run(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
