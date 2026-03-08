# ⛅ SkyWatch – Weather Forecasting System

**🌐 Live Demo → [https://osman-builds.github.io/weather-forecasting-system/](https://osman-builds.github.io/weather-forecasting-system/)**

A full-stack weather forecasting system: a beautiful, responsive **web app** deployed to GitHub Pages and a production-ready **REST API** built with Python and FastAPI.

![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-a78bfa?style=for-the-badge&logo=github)
![Backend API](https://img.shields.io/badge/Backend%20API-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)

---

## 🖥️ Web App (Live)

The web app is deployed at:

> **https://osman-builds.github.io/weather-forecasting-system/**

Features:
- 🔍 Search any city worldwide
- 📍 One-click geolocation
- 🌡️ Current conditions (temperature, humidity, wind, pressure, cloud cover)
- 📅 7-day daily forecast with icons and precipitation
- ☀️ UV index, sunrise/sunset, wind gusts
- 🔄 Toggle between Celsius and Fahrenheit
- 📱 Fully responsive – works on mobile, tablet, and desktop
- ⚡ Instant load – uses [Open-Meteo](https://open-meteo.com) (free, no API key required)

---

## 🏗️ Architecture

```
├── frontend/              ← Web app (deployed to GitHub Pages)
│   └── index.html         ← Single-page app (HTML/CSS/JS, Open-Meteo API)
│
├── src/                   ← Python FastAPI backend
│   ├── api/
│   │   ├── main.py        # FastAPI application
│   │   └── routes/
│   │       ├── weather.py # GET /api/v1/weather/current
│   │       └── forecast.py# GET /api/v1/forecast/
│   ├── services/
│   │   ├── ingestion.py   # OpenWeatherMap data fetching (with mock fallback)
│   │   ├── processor.py   # Enriches observations (dew point, heat index, etc.)
│   │   └── forecaster.py  # 7-day forecast generation
│   ├── models/
│   │   ├── weather.py     # WeatherObservation, Coordinates, WeatherCondition
│   │   └── forecast.py    # Forecast, DailyForecast
│   └── config.py          # Pydantic-settings configuration
│
├── tests/                 ← 53 unit & integration tests
├── .github/workflows/
│   └── deploy-pages.yml   ← Deploys frontend to GitHub Pages on push
├── Dockerfile             ← Container for backend API
├── docker-compose.yml     ← Docker Compose for local development
└── render.yaml            ← One-click backend deploy on Render.com
```

---

## �� Deploying the Backend API

### Option 1 – Render.com (one-click, free)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repository
2. Go to [render.com](https://render.com) → New → Web Service → connect your fork
3. Render auto-detects `render.yaml` and deploys the API
4. (Optional) Set `OPENWEATHER_API_KEY` in Render's Environment settings for live data

### Option 2 – Docker

```bash
# With Docker Compose
docker compose up

# Or build and run directly
docker build -t skywatch-api .
docker run -p 8000:8000 -e OPENWEATHER_API_KEY=your_key skywatch-api
```

### Option 3 – Local (no Docker)

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

---

## 🔌 Backend API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info & status |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/weather/current` | Current weather conditions |
| `GET` | `/api/v1/forecast/` | Multi-day weather forecast |

### Query Parameters

**`/api/v1/weather/current`**

| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | string | City name (e.g. `London`) |
| `lat` | float | Latitude (-90 to 90) |
| `lon` | float | Longitude (-180 to 180) |
| `units` | string | `metric` (default), `imperial`, or `standard` |

**`/api/v1/forecast/`**

| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | string | City name |
| `lat` / `lon` | float | Coordinates |
| `days` | int | Days to forecast (1–7, default: 7) |

### Example Requests

```bash
# Current weather
curl "http://localhost:8000/api/v1/weather/current?city=London"

# Forecast (imperial units)
curl "http://localhost:8000/api/v1/weather/current?lat=51.5&lon=-0.1&units=imperial"

# 5-day forecast
curl "http://localhost:8000/api/v1/forecast/?city=Tokyo&days=5"
```

---

## 🧪 Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

53 tests covering models, services, and API endpoints.

---

## 🌐 Deployment Targets

| Component | Platform | URL |
|-----------|----------|-----|
| Web App | GitHub Pages | https://osman-builds.github.io/weather-forecasting-system/ |
| Backend API | Render.com / Docker | Deploy via `render.yaml` or `docker-compose.yml` |

---

## 📄 License

Licensed under the GNU General Public License v3.0 – see [LICENSE](LICENSE) for details.
