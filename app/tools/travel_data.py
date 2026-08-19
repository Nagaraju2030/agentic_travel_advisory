from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.config import settings
from app.models.schemas import Evidence, TripRequest
from app.tools.http import AsyncHttpClient


class TravelDataTools:
    """Small live-data toolset with graceful fallbacks.

    No API keys are required for Open-Meteo or REST Countries. Time-sensitive
    legal/safety/health decisions are intentionally surfaced as verification
    tasks instead of being invented from non-authoritative data.
    """

    def __init__(self) -> None:
        self.http = AsyncHttpClient()

    async def geocode(self, place: str) -> tuple[dict[str, Any], list[Evidence]]:
        if not settings.enable_live_tools:
            return {}, []
        try:
            payload = await self.http.get_json(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": place, "count": 1, "language": "en", "format": "json"},
            )
            row = (payload.get("results") or [{}])[0]
            if not row:
                return {}, []
            data = {
                "name": row.get("name"),
                "country": row.get("country"),
                "country_code": row.get("country_code"),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "timezone": row.get("timezone"),
            }
            ev = Evidence(
                source="Open-Meteo Geocoding",
                detail=f"Resolved destination to {data.get('name')}, {data.get('country')}.",
                url="https://open-meteo.com/",
            )
            return data, [ev]
        except Exception:
            return {}, []

    async def weather(self, request: TripRequest) -> tuple[dict[str, Any], list[Evidence]]:
        geo, geo_evidence = await self.geocode(request.destination)
        if not geo.get("latitude"):
            return {"available": False, "reason": "Destination could not be geocoded."}, geo_evidence
        if not settings.enable_live_tools:
            return {"available": False, "reason": "Live tools disabled."}, geo_evidence

        try:
            payload = await self.http.get_json(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": geo["latitude"],
                    "longitude": geo["longitude"],
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": "auto",
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat(),
                },
            )
            daily = payload.get("daily", {})
            data = {
                "available": bool(daily.get("time")),
                "timezone": payload.get("timezone"),
                "days": [
                    {
                        "date": d,
                        "temp_max_c": tmax,
                        "temp_min_c": tmin,
                        "precipitation_probability_pct": rain,
                        "weather_code": code,
                    }
                    for d, tmax, tmin, rain, code in zip(
                        daily.get("time", []),
                        daily.get("temperature_2m_max", []),
                        daily.get("temperature_2m_min", []),
                        daily.get("precipitation_probability_max", []),
                        daily.get("weather_code", []),
                    )
                ],
            }
            evidence = geo_evidence + [
                Evidence(
                    source="Open-Meteo Forecast",
                    detail="Daily forecast retrieved for the requested trip dates when within provider forecast horizon.",
                    url="https://open-meteo.com/",
                )
            ]
            return data, evidence
        except Exception as exc:
            return {"available": False, "reason": f"Forecast unavailable: {type(exc).__name__}"}, geo_evidence

    async def country_profile(self, destination: str) -> tuple[dict[str, Any], list[Evidence]]:
        geo, geo_evidence = await self.geocode(destination)
        code = geo.get("country_code")
        if not code or not settings.enable_live_tools:
            return {"geocoding": geo}, geo_evidence
        try:
            payload = await self.http.get_json(f"https://restcountries.com/v3.1/alpha/{code}")
            row = payload[0] if isinstance(payload, list) and payload else {}
            currencies = list((row.get("currencies") or {}).keys())
            languages = list((row.get("languages") or {}).values())
            data = {
                "country": (row.get("name") or {}).get("common") or geo.get("country"),
                "capital": (row.get("capital") or [None])[0],
                "region": row.get("region"),
                "subregion": row.get("subregion"),
                "currencies": currencies,
                "languages": languages,
                "calling_codes": [
                    f"{(row.get('idd') or {}).get('root', '')}{suffix}"
                    for suffix in ((row.get('idd') or {}).get('suffixes') or [])
                ],
                "timezones": row.get("timezones") or [],
                "geocoding": geo,
            }
            return data, geo_evidence + [
                Evidence(
                    source="REST Countries",
                    detail=f"Country metadata retrieved for {data.get('country')}.",
                    url="https://restcountries.com/",
                )
            ]
        except Exception:
            return {"geocoding": geo}, geo_evidence

    @staticmethod
    def authoritative_verification_tasks(destination: str) -> list[str]:
        return [
            f"Check the official immigration/embassy source for entry, visa, passport-validity and transit rules for {destination}.",
            f"Check your government's current travel advisory for {destination} before departure.",
            "Check airline/transit-country documentation requirements before ticketing and again before departure.",
            "Check official public-health guidance and travel insurance coverage for your itinerary.",
        ]
