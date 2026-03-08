from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class WeatherCondition(BaseModel):
    id: int = Field(..., description="Weather condition code")
    main: str = Field(..., description="Weather condition group (e.g. Rain, Snow)")
    description: str = Field(..., description="Human-readable description")
    icon: str = Field(..., description="Weather icon identifier")


class WeatherObservation(BaseModel):
    location: str = Field(..., description="City or location name")
    coordinates: Coordinates
    timestamp: datetime = Field(..., description="Observation timestamp (UTC)")
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    feels_like_celsius: float = Field(..., description="Feels-like temperature in Celsius")
    humidity_percent: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    pressure_hpa: float = Field(..., description="Atmospheric pressure (hPa)")
    wind_speed_ms: float = Field(..., ge=0, description="Wind speed (m/s)")
    wind_direction_degrees: Optional[float] = Field(
        None, ge=0, lt=360, description="Wind direction (degrees)"
    )
    visibility_meters: Optional[float] = Field(None, ge=0, description="Visibility (m)")
    cloudiness_percent: float = Field(..., ge=0, le=100, description="Cloudiness (%)")
    conditions: list[WeatherCondition] = Field(default_factory=list)

    @property
    def temperature_fahrenheit(self) -> float:
        return self.temperature_celsius * 9 / 5 + 32
