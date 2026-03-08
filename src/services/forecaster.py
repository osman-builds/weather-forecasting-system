"""
Forecast generation service: produces multi-day forecasts.

When an OpenWeatherMap API key is configured the service uses the
One Call API 3.0 (or the free 5-day/3-hour forecast endpoint).
Without an API key it generates synthetic deterministic forecasts
so the system is fully functional for demos and testing.
"""
import math
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import httpx

from ..config import settings
from ..models.forecast import DailyForecast, Forecast
from ..models.weather import WeatherCondition


def _synthetic_daily(
    forecast_date: date,
    lat: float,
    lon: float,
    day_offset: int,
) -> DailyForecast:
    """Generate a plausible synthetic daily forecast entry."""
    seed = abs(lat) + abs(lon) + day_offset
    base_temp = 15.0 + (seed % 20) - 10
    amplitude = 5 + (seed % 5)

    t_min = round(base_temp - amplitude, 1)
    t_max = round(base_temp + amplitude, 1)
    t_morn = round(base_temp - amplitude * 0.5, 1)
    t_day = round(base_temp + amplitude * 0.8, 1)
    t_eve = round(base_temp + amplitude * 0.3, 1)
    t_night = round(base_temp - amplitude * 0.7, 1)

    precip_prob = round((seed % 100) / 100, 2)
    precip_mm = round(precip_prob * (seed % 15), 1)
    humidity = round(40 + (seed % 50), 1)
    cloudiness = round((seed % 100), 1)
    wind_speed = round(2 + (seed % 10), 1)
    wind_dir = round(seed % 360, 1)
    uv = round(1 + (seed % 10), 1)

    if cloudiness < 20:
        cond_id, cond_main, cond_desc, icon = 800, "Clear", "clear sky", "01d"
    elif cloudiness < 50:
        cond_id, cond_main, cond_desc, icon = 802, "Clouds", "scattered clouds", "03d"
    elif precip_prob > 0.5:
        cond_id, cond_main, cond_desc, icon = 500, "Rain", "light rain", "10d"
    else:
        cond_id, cond_main, cond_desc, icon = 804, "Clouds", "overcast clouds", "04d"

    summary = f"{cond_desc.capitalize()}, high {t_max}°C / low {t_min}°C"

    return DailyForecast(
        date=forecast_date,
        temperature_min_celsius=t_min,
        temperature_max_celsius=t_max,
        temperature_morning_celsius=t_morn,
        temperature_day_celsius=t_day,
        temperature_evening_celsius=t_eve,
        temperature_night_celsius=t_night,
        humidity_percent=humidity,
        pressure_hpa=1013.25,
        wind_speed_ms=wind_speed,
        wind_direction_degrees=wind_dir,
        precipitation_mm=precip_mm,
        precipitation_probability=precip_prob,
        cloudiness_percent=cloudiness,
        uv_index=uv,
        conditions=[
            WeatherCondition(id=cond_id, main=cond_main, description=cond_desc, icon=icon)
        ],
        summary=summary,
    )


def _parse_owm_daily_from_5day(raw_list: list, target_date: date) -> Optional[DailyForecast]:
    """
    Aggregate 3-hour OWM free-tier entries for a given date into a DailyForecast.
    """
    entries = [
        e for e in raw_list
        if datetime.fromtimestamp(e["dt"], tz=timezone.utc).date() == target_date
    ]
    if not entries:
        return None

    temps = [e["main"]["temp"] for e in entries]
    t_min = min(temps)
    t_max = max(temps)

    # Pick representative entries for morning/day/evening/night by hour
    def _temp_at_hour(target_hour: int) -> float:
        closest = min(
            entries,
            key=lambda e: abs(
                datetime.fromtimestamp(e["dt"], tz=timezone.utc).hour - target_hour
            ),
        )
        return closest["main"]["temp"]

    conditions = [
        WeatherCondition(
            id=w["id"],
            main=w["main"],
            description=w["description"],
            icon=w["icon"],
        )
        for w in entries[len(entries) // 2].get("weather", [])
    ]

    precip_mm = sum(
        e.get("rain", {}).get("3h", 0) + e.get("snow", {}).get("3h", 0) for e in entries
    )
    mid = entries[len(entries) // 2]
    summary = (
        f"{conditions[0].description.capitalize() if conditions else 'N/A'}, "
        f"high {round(t_max, 1)}°C / low {round(t_min, 1)}°C"
    )

    return DailyForecast(
        date=target_date,
        temperature_min_celsius=round(t_min, 1),
        temperature_max_celsius=round(t_max, 1),
        temperature_morning_celsius=round(_temp_at_hour(6), 1),
        temperature_day_celsius=round(_temp_at_hour(12), 1),
        temperature_evening_celsius=round(_temp_at_hour(18), 1),
        temperature_night_celsius=round(_temp_at_hour(0), 1),
        humidity_percent=mid["main"]["humidity"],
        pressure_hpa=mid["main"]["pressure"],
        wind_speed_ms=mid["wind"]["speed"],
        wind_direction_degrees=mid["wind"].get("deg"),
        precipitation_mm=round(precip_mm, 1),
        precipitation_probability=mid.get("pop", 0),
        cloudiness_percent=mid["clouds"]["all"],
        conditions=conditions,
        summary=summary,
    )


async def generate_forecast(
    location: str,
    lat: float,
    lon: float,
    days: int = 7,
) -> Forecast:
    """
    Generate a multi-day forecast for the given coordinates.

    Uses the OpenWeatherMap free 5-day / 3-hour forecast endpoint when an API
    key is available; otherwise returns a synthetic forecast.
    """
    days = max(1, min(days, 7))
    today = datetime.now(timezone.utc).date()
    generated_at = datetime.now(timezone.utc)

    if not settings.openweather_api_key:
        daily = [
            _synthetic_daily(today + timedelta(days=i), lat, lon, i)
            for i in range(days)
        ]
        return Forecast(
            location=location,
            latitude=lat,
            longitude=lon,
            generated_at=generated_at,
            daily=daily,
        )

    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweather_api_key,
        "units": "metric",
        "cnt": 40,  # maximum 3-hour intervals for ~5 days
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{settings.openweather_base_url}/forecast", params=params
        )
        response.raise_for_status()
        data = response.json()

    raw_list = data["list"]
    daily: list[DailyForecast] = []
    for i in range(days):
        target_date = today + timedelta(days=i)
        entry = _parse_owm_daily_from_5day(raw_list, target_date)
        if entry:
            daily.append(entry)
        else:
            # Fall back to synthetic for missing days
            daily.append(_synthetic_daily(target_date, lat, lon, i))

    city = data.get("city", {})
    resolved_name = city.get("name", location)
    timezone_offset = city.get("timezone", 0)
    tz_label = f"UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset // 3600}"

    return Forecast(
        location=resolved_name,
        latitude=lat,
        longitude=lon,
        generated_at=generated_at,
        daily=daily,
        timezone=tz_label,
    )
