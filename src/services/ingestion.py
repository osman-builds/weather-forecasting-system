"""
Data ingestion service: fetches weather data from OpenWeatherMap API.
Falls back to synthetic mock data when no API key is configured.
"""
import math
from datetime import datetime, timezone
from typing import Optional

import httpx

from ..config import settings
from ..models.weather import Coordinates, WeatherCondition, WeatherObservation


def _mock_observation(location: str, lat: float, lon: float) -> WeatherObservation:
    """Return a deterministic synthetic observation for testing / demo use."""
    # Use position to vary the mock values so different locations differ
    seed = abs(lat) + abs(lon)
    temp = 15.0 + (seed % 20) - 10  # range roughly -10 to 30°C
    return WeatherObservation(
        location=location,
        coordinates=Coordinates(latitude=lat, longitude=lon),
        timestamp=datetime.now(timezone.utc),
        temperature_celsius=round(temp, 1),
        feels_like_celsius=round(temp - 2, 1),
        humidity_percent=round(50 + (seed % 40), 1),
        pressure_hpa=1013.25,
        wind_speed_ms=round(3 + (seed % 7), 1),
        wind_direction_degrees=round(seed % 360, 1),
        visibility_meters=10000,
        cloudiness_percent=round(seed % 100, 1),
        conditions=[
            WeatherCondition(
                id=800,
                main="Clear",
                description="clear sky",
                icon="01d",
            )
        ],
    )


async def fetch_current_weather(
    location: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> WeatherObservation:
    """
    Fetch the current weather observation for a location.

    Parameters
    ----------
    location:
        Human-readable city/location name used when no API key is set.
    lat, lon:
        If provided, query by coordinates; otherwise query by city name.
    """
    if not settings.openweather_api_key:
        # No API key – return mock data so the system is usable without a key
        _lat = lat if lat is not None else 0.0
        _lon = lon if lon is not None else 0.0
        return _mock_observation(location, _lat, _lon)

    params: dict = {"appid": settings.openweather_api_key, "units": "metric"}
    if lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon
    else:
        params["q"] = location

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{settings.openweather_base_url}/weather", params=params
        )
        response.raise_for_status()
        data = response.json()

    coord = data["coord"]
    conditions = [
        WeatherCondition(
            id=w["id"],
            main=w["main"],
            description=w["description"],
            icon=w["icon"],
        )
        for w in data.get("weather", [])
    ]

    return WeatherObservation(
        location=data.get("name", location),
        coordinates=Coordinates(latitude=coord["lat"], longitude=coord["lon"]),
        timestamp=datetime.fromtimestamp(data["dt"], tz=timezone.utc),
        temperature_celsius=data["main"]["temp"],
        feels_like_celsius=data["main"]["feels_like"],
        humidity_percent=data["main"]["humidity"],
        pressure_hpa=data["main"]["pressure"],
        wind_speed_ms=data["wind"]["speed"],
        wind_direction_degrees=data["wind"].get("deg"),
        visibility_meters=data.get("visibility"),
        cloudiness_percent=data["clouds"]["all"],
        conditions=conditions,
    )
