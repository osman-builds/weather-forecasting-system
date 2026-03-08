"""Integration tests for the REST API."""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestCurrentWeather:
    def test_by_city(self):
        resp = client.get("/api/v1/weather/current?city=London")
        assert resp.status_code == 200
        data = resp.json()
        assert "temperature_celsius" in data
        assert "humidity_percent" in data
        assert "wind_speed_ms" in data
        assert "dew_point_celsius" in data

    def test_by_coordinates(self):
        resp = client.get("/api/v1/weather/current?lat=51.5&lon=-0.1")
        assert resp.status_code == 200
        data = resp.json()
        assert "temperature_celsius" in data

    def test_missing_params_returns_422(self):
        resp = client.get("/api/v1/weather/current")
        assert resp.status_code == 422

    def test_invalid_lat(self):
        resp = client.get("/api/v1/weather/current?lat=999&lon=0")
        assert resp.status_code == 422

    def test_units_metric(self):
        resp = client.get("/api/v1/weather/current?city=Paris&units=metric")
        assert resp.status_code == 200
        assert resp.json()["units"] == "metric"

    def test_units_imperial(self):
        resp = client.get("/api/v1/weather/current?city=Paris&units=imperial")
        assert resp.status_code == 200
        assert resp.json()["units"] == "imperial"

    def test_units_standard(self):
        resp = client.get("/api/v1/weather/current?city=Paris&units=standard")
        assert resp.status_code == 200
        assert resp.json()["units"] == "kelvin"

    def test_invalid_units(self):
        resp = client.get("/api/v1/weather/current?city=Paris&units=banana")
        assert resp.status_code == 422


class TestForecast:
    def test_by_city(self):
        resp = client.get("/api/v1/forecast/?city=Berlin")
        assert resp.status_code == 200
        data = resp.json()
        assert data["location"] == "Berlin"
        assert len(data["daily"]) == 7

    def test_by_coordinates(self):
        resp = client.get("/api/v1/forecast/?lat=52.5&lon=13.4")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["daily"]) == 7

    def test_days_param(self):
        resp = client.get("/api/v1/forecast/?city=Tokyo&days=3")
        assert resp.status_code == 200
        assert len(resp.json()["daily"]) == 3

    def test_days_exceeds_max(self):
        resp = client.get("/api/v1/forecast/?city=Tokyo&days=10")
        assert resp.status_code == 422

    def test_missing_params_returns_422(self):
        resp = client.get("/api/v1/forecast/")
        assert resp.status_code == 422

    def test_daily_fields(self):
        resp = client.get("/api/v1/forecast/?city=Sydney&days=1")
        assert resp.status_code == 200
        day = resp.json()["daily"][0]
        assert "temperature_min_celsius" in day
        assert "temperature_max_celsius" in day
        assert "precipitation_probability" in day
        assert "conditions" in day
