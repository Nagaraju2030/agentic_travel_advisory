from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Dependency-aware multi-agent travel advisory API with 13 specialized agents.",
)
app.include_router(router)


@app.get("/")
async def root() -> dict:
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/v1/health",
        "agents": "/v1/agents",
        "advisory": "/v1/advisory",
    }
