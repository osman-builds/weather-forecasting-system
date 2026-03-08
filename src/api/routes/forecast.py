from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ...services.ingestion import fetch_current_weather
from ...services.forecaster import generate_forecast
from ...models.forecast import Forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get(
    "/",
    response_model=Forecast,
    summary="Get multi-day forecast",
    description=(
        "Returns a daily weather forecast for up to 7 days. "
        "Supply either `city` or both `lat` and `lon`."
    ),
)
async def get_forecast(
    city: Optional[str] = Query(None, description="City name (e.g. Tokyo)"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude"),
    days: int = Query(7, ge=1, le=7, description="Number of days (1-7)"),
):
    if city is None and (lat is None or lon is None):
        raise HTTPException(
            status_code=422,
            detail="Provide either 'city' or both 'lat' and 'lon'.",
        )

    # Resolve coordinates from city name when only the name is supplied
    if city is not None and (lat is None or lon is None):
        try:
            obs = await fetch_current_weather(location=city)
            lat = obs.coordinates.latitude
            lon = obs.coordinates.longitude
        except Exception as exc:
            raise HTTPException(
                status_code=502, detail=f"Could not resolve city coordinates: {exc}"
            ) from exc

    location = city or f"{lat},{lon}"
    try:
        forecast = await generate_forecast(location=location, lat=lat, lon=lon, days=days)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Forecast unavailable: {exc}") from exc

    return forecast
