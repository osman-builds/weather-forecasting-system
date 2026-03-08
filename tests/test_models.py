"""Tests for data models."""
from datetime import date, datetime, timezone

import pytest

from src.models.weather import Coordinates, WeatherCondition, WeatherObservation
from src.models.forecast import DailyForecast, Forecast


class TestCoordinates:
    def test_valid(self):
        c = Coordinates(latitude=51.5, longitude=-0.1)
        assert c.latitude == 51.5
        assert c.longitude == -0.1

    def test_invalid_latitude(self):
        with pytest.raises(Exception):
            Coordinates(latitude=91, longitude=0)

    def test_invalid_longitude(self):
        with pytest.raises(Exception):
            Coordinates(latitude=0, longitude=181)


class TestWeatherObservation:
    def _make(self, **overrides):
        defaults = dict(
            location="London",
            coordinates=Coordinates(latitude=51.5, longitude=-0.1),
            timestamp=datetime.now(timezone.utc),
            temperature_celsius=15.0,
            feels_like_celsius=13.0,
            humidity_percent=70.0,
            pressure_hpa=1013.0,
            wind_speed_ms=5.0,
            cloudiness_percent=40.0,
        )
        defaults.update(overrides)
        return WeatherObservation(**defaults)

    def test_temperature_fahrenheit(self):
        obs = self._make(temperature_celsius=0.0)
        assert obs.temperature_fahrenheit == 32.0

    def test_temperature_fahrenheit_100c(self):
        obs = self._make(temperature_celsius=100.0)
        assert obs.temperature_fahrenheit == 212.0

    def test_humidity_bounds(self):
        with pytest.raises(Exception):
            self._make(humidity_percent=101)

    def test_optional_fields_none(self):
        obs = self._make()
        assert obs.wind_direction_degrees is None
        assert obs.visibility_meters is None


class TestDailyForecast:
    def _make(self, **overrides):
        defaults = dict(
            date=date.today(),
            temperature_min_celsius=5.0,
            temperature_max_celsius=20.0,
            temperature_morning_celsius=8.0,
            temperature_day_celsius=18.0,
            temperature_evening_celsius=15.0,
            temperature_night_celsius=7.0,
            humidity_percent=60.0,
            pressure_hpa=1013.0,
            wind_speed_ms=3.0,
            cloudiness_percent=25.0,
        )
        defaults.update(overrides)
        return DailyForecast(**defaults)

    def test_defaults(self):
        df = self._make()
        assert df.precipitation_mm == 0.0
        assert df.precipitation_probability == 0.0
        assert df.conditions == []
        assert df.summary == ""

    def test_precipitation_probability_bounds(self):
        with pytest.raises(Exception):
            self._make(precipitation_probability=1.5)


class TestForecast:
    def test_basic(self):
        daily = [
            DailyForecast(
                date=date.today(),
                temperature_min_celsius=5.0,
                temperature_max_celsius=15.0,
                temperature_morning_celsius=7.0,
                temperature_day_celsius=14.0,
                temperature_evening_celsius=12.0,
                temperature_night_celsius=6.0,
                humidity_percent=65.0,
                pressure_hpa=1015.0,
                wind_speed_ms=4.0,
                cloudiness_percent=30.0,
            )
        ]
        f = Forecast(
            location="Berlin",
            latitude=52.5,
            longitude=13.4,
            generated_at=datetime.now(timezone.utc),
            daily=daily,
        )
        assert f.location == "Berlin"
        assert len(f.daily) == 1
        assert f.timezone == "UTC"
