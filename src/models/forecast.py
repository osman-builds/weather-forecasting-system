from datetime import date as _date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .weather import WeatherCondition


class DailyForecast(BaseModel):
    date: _date = Field(..., description="Forecast date")
    temperature_min_celsius: float = Field(..., description="Minimum temperature (°C)")
    temperature_max_celsius: float = Field(..., description="Maximum temperature (°C)")
    temperature_morning_celsius: float = Field(..., description="Morning temperature (°C)")
    temperature_day_celsius: float = Field(..., description="Daytime temperature (°C)")
    temperature_evening_celsius: float = Field(..., description="Evening temperature (°C)")
    temperature_night_celsius: float = Field(..., description="Night temperature (°C)")
    humidity_percent: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    pressure_hpa: float = Field(..., description="Atmospheric pressure (hPa)")
    wind_speed_ms: float = Field(..., ge=0, description="Wind speed (m/s)")
    wind_direction_degrees: Optional[float] = Field(None, ge=0, lt=360)
    precipitation_mm: float = Field(default=0.0, ge=0, description="Precipitation (mm)")
    precipitation_probability: float = Field(
        default=0.0, ge=0, le=1, description="Precipitation probability (0-1)"
    )
    cloudiness_percent: float = Field(..., ge=0, le=100, description="Cloudiness (%)")
    uv_index: Optional[float] = Field(None, ge=0, description="UV index")
    conditions: list[WeatherCondition] = Field(default_factory=list)
    summary: str = Field(default="", description="Human-readable daily summary")


class Forecast(BaseModel):
    location: str = Field(..., description="City or location name")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    generated_at: datetime = Field(..., description="When this forecast was generated (UTC)")
    daily: list[DailyForecast] = Field(..., description="Daily forecasts")
    timezone: str = Field(default="UTC", description="Timezone of the location")
