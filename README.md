# Weather Forecasting System

A modular, production-ready weather forecasting system built with Python and FastAPI. It provides current weather conditions and multi-day forecasts for any location worldwide via a clean REST API.

## Features

- **Current weather** – temperature, humidity, wind, pressure, visibility, and cloud cover for any city or coordinates
- **7-day forecast** – daily min/max temperatures, precipitation probability, UV index, and weather conditions
- **Enriched responses** – derived fields including dew point, heat index, wind cardinal direction, and unit conversions (metric, imperial, standard)
- **OpenWeatherMap integration** – live data when an API key is supplied; deterministic synthetic data for demos and testing when no key is set
- **OpenAPI docs** – interactive Swagger UI at `/docs` and ReDoc at `/redoc`
- **Docker support** – single-command deployment via Docker Compose

## Architecture

```
src/
├── api/
│   ├── main.py            # FastAPI application factory
│   └── routes/
│       ├── weather.py     # GET /api/v1/weather/current
│       └── forecast.py    # GET /api/v1/forecast/
├── services/
│   ├── ingestion.py       # Fetches raw data from OpenWeatherMap (or mock)
│   ├── processor.py       # Enriches observations with derived metrics
│   └── forecaster.py      # Generates multi-day forecasts
├── models/
│   ├── weather.py         # WeatherObservation, WeatherCondition, Coordinates
│   └── forecast.py        # Forecast, DailyForecast
└── config.py              # Pydantic-settings configuration
tests/
├── test_models.py
├── test_processor.py
├── test_forecaster.py
└── test_api.py
```

## Quick Start

### Without Docker

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

Open http://localhost:8000/docs for the interactive API documentation.

### With Docker

```bash
docker compose up
```

### With a live API key

Create a `.env` file (or export the variable) before starting:

```
OPENWEATHER_API_KEY=your_key_here
```

Free API keys are available at https://openweathermap.org/api.

## API Endpoints

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

Supply either `city` **or** both `lat` and `lon`.

**`/api/v1/forecast/`**

| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | string | City name |
| `lat` | float | Latitude |
| `lon` | float | Longitude |
| `days` | int | Number of days 1–7 (default: 7) |

### Example Requests

```bash
# Current weather by city
curl "http://localhost:8000/api/v1/weather/current?city=London"

# Current weather by coordinates (imperial units)
curl "http://localhost:8000/api/v1/weather/current?lat=51.5&lon=-0.1&units=imperial"

# 5-day forecast
curl "http://localhost:8000/api/v1/forecast/?city=Tokyo&days=5"
```

## Running Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## License

This project is licensed under the GNU General Public License v3.0 – see [LICENSE](LICENSE) for details.
