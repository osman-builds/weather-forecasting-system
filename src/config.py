from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenWeatherMap API key (set via environment variable OPENWEATHER_API_KEY)
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"

    # API settings
    api_title: str = "Weather Forecasting System"
    api_version: str = "1.0.0"
    api_description: str = (
        "A weather forecasting system that provides current conditions "
        "and multi-day forecasts for locations worldwide."
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
