from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ...services.ingestion import fetch_current_weather
from ...services.processor import enrich_observation

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get(
    "/current",
    summary="Get current weather",
    description=(
        "Returns the current weather conditions for a city name or geographic coordinates. "
        "Supply either `city` or both `lat` and `lon`."
    ),
)
async def get_current_weather(
    city: Optional[str] = Query(None, description="City name (e.g. London)"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude"),
    units: str = Query("metric", pattern="^(metric|imperial|standard)$"),
):
    if city is None and (lat is None or lon is None):
        raise HTTPException(
            status_code=422,
            detail="Provide either 'city' or both 'lat' and 'lon'.",
        )

    location = city or f"{lat},{lon}"
    try:
        obs = await fetch_current_weather(location=location, lat=lat, lon=lon)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather data unavailable: {exc}") from exc

    data = enrich_observation(obs)

    # Unit conversions when imperial or standard is requested
    if units == "imperial":
        data["temperature_celsius"] = data.pop("temperature_fahrenheit")
        data["feels_like_celsius"] = data.pop("feels_like_fahrenheit")
        data["wind_speed_ms"] = data.pop("wind_speed_mph")
        data["units"] = "imperial"
    elif units == "standard":
        data["temperature_celsius"] = round(obs.temperature_celsius + 273.15, 2)
        data["feels_like_celsius"] = round(obs.feels_like_celsius + 273.15, 2)
        data["units"] = "kelvin"
    else:
        data["units"] = "metric"

    return data
