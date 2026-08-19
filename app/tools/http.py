from __future__ import annotations

import asyncio

import httpx

from app.core.config import settings


class AsyncHttpClient:
    def __init__(self) -> None:
        self.timeout = settings.http_timeout_seconds

    async def get_json(self, url: str, params: dict | None = None) -> dict:
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    await asyncio.sleep(0.35)
        assert last_error is not None
        raise last_error
