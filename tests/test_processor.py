"""Tests for data processing / enrichment service."""
import pytest

from src.services.processor import (
    celsius_to_fahrenheit,
    ms_to_kmh,
    ms_to_mph,
    hpa_to_inhg,
    wind_degrees_to_cardinal,
    compute_dew_point,
    compute_heat_index,
    enrich_observation,
)
from src.models.weather import Coordinates, WeatherObservation
from datetime import datetime, timezone


def _obs(**overrides):
    defaults = dict(
        location="Test City",
        coordinates=Coordinates(latitude=10.0, longitude=20.0),
        timestamp=datetime.now(timezone.utc),
        temperature_celsius=20.0,
        feels_like_celsius=18.0,
        humidity_percent=50.0,
        pressure_hpa=1013.25,
        wind_speed_ms=5.0,
        wind_direction_degrees=180.0,
        cloudiness_percent=30.0,
    )
    defaults.update(overrides)
    return WeatherObservation(**defaults)


class TestUnitConversions:
    def test_celsius_to_fahrenheit_freezing(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_celsius_to_fahrenheit_boiling(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_ms_to_kmh(self):
        assert ms_to_kmh(1) == pytest.approx(3.6)

    def test_ms_to_mph(self):
        assert ms_to_mph(1) == pytest.approx(2.237)

    def test_hpa_to_inhg(self):
        assert hpa_to_inhg(1013.25) == pytest.approx(29.921, abs=0.01)


class TestWindCardinal:
    @pytest.mark.parametrize(
        "degrees,expected",
        [
            (0, "N"),
            (45, "NE"),
            (90, "E"),
            (135, "SE"),
            (180, "S"),
            (225, "SW"),
            (270, "W"),
            (315, "NW"),
            (359, "N"),
        ],
    )
    def test_cardinal(self, degrees, expected):
        assert wind_degrees_to_cardinal(degrees) == expected


class TestDerivedMetrics:
    def test_dew_point_at_100_humidity(self):
        # At 100% humidity dew point equals temperature
        dp = compute_dew_point(20.0, 100.0)
        assert dp == pytest.approx(20.0, abs=0.5)

    def test_dew_point_at_low_humidity(self):
        dp = compute_dew_point(30.0, 20.0)
        assert dp < 30.0

    def test_heat_index_hot(self):
        hi = compute_heat_index(35.0, 80.0)
        assert hi > 35.0


class TestEnrichObservation:
    def test_contains_derived_fields(self):
        obs = _obs(temperature_celsius=20.0, wind_direction_degrees=270.0)
        data = enrich_observation(obs)
        assert "temperature_fahrenheit" in data
        assert "wind_speed_kmh" in data
        assert "dew_point_celsius" in data
        assert data["wind_direction_cardinal"] == "W"

    def test_heat_index_added_above_27c(self):
        obs = _obs(temperature_celsius=30.0, humidity_percent=80.0)
        data = enrich_observation(obs)
        assert "heat_index_celsius" in data

    def test_no_heat_index_below_27c(self):
        obs = _obs(temperature_celsius=20.0, humidity_percent=80.0)
        data = enrich_observation(obs)
        assert "heat_index_celsius" not in data

    def test_no_cardinal_without_direction(self):
        obs = _obs(wind_direction_degrees=None)
        data = enrich_observation(obs)
        assert "wind_direction_cardinal" not in data
