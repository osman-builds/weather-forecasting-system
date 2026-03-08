"""Tests for the forecaster service (synthetic / no-API-key path)."""
import pytest
from datetime import date

from src.services.forecaster import generate_forecast, _synthetic_daily


class TestSyntheticDaily:
    def test_returns_daily_forecast(self):
        df = _synthetic_daily(date.today(), lat=51.5, lon=-0.1, day_offset=0)
        assert df.date == date.today()
        assert df.temperature_min_celsius <= df.temperature_max_celsius
        assert 0 <= df.humidity_percent <= 100
        assert 0 <= df.cloudiness_percent <= 100
        assert df.precipitation_probability >= 0
        assert len(df.conditions) == 1

    def test_different_offsets_differ(self):
        d = date.today()
        df0 = _synthetic_daily(d, lat=10.0, lon=20.0, day_offset=0)
        df1 = _synthetic_daily(d, lat=10.0, lon=20.0, day_offset=3)
        # Not identical (different seed)
        assert df0.temperature_max_celsius != df1.temperature_max_celsius


@pytest.mark.asyncio
class TestGenerateForecast:
    async def test_returns_forecast(self):
        forecast = await generate_forecast("TestCity", lat=51.5, lon=-0.1, days=3)
        assert forecast.location == "TestCity"
        assert len(forecast.daily) == 3

    async def test_days_clamped_to_7(self):
        forecast = await generate_forecast("Anywhere", lat=0, lon=0, days=10)
        assert len(forecast.daily) == 7

    async def test_days_clamped_to_1(self):
        forecast = await generate_forecast("Anywhere", lat=0, lon=0, days=0)
        assert len(forecast.daily) == 1

    async def test_ascending_dates(self):
        forecast = await generate_forecast("Anywhere", lat=0, lon=0, days=5)
        dates = [d.date for d in forecast.daily]
        assert dates == sorted(dates)
