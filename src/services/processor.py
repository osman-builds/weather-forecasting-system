"""
Data processing service: normalises and enriches raw weather observations.
"""
from ..models.weather import WeatherObservation


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def ms_to_kmh(ms: float) -> float:
    return ms * 3.6


def ms_to_mph(ms: float) -> float:
    return ms * 2.237


def hpa_to_inhg(hpa: float) -> float:
    return hpa * 0.02953


def wind_degrees_to_cardinal(degrees: float) -> str:
    """Convert a wind bearing (0-360°) to a 16-point cardinal direction."""
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]


def compute_dew_point(temp_celsius: float, humidity_percent: float) -> float:
    """
    Approximate dew point using the Magnus formula.
    Returns dew point in Celsius.
    """
    import math
    a, b = 17.27, 237.7
    alpha = (a * temp_celsius) / (b + temp_celsius) + math.log(humidity_percent / 100.0)
    return round((b * alpha) / (a - alpha), 2)


def compute_heat_index(temp_celsius: float, humidity_percent: float) -> float:
    """
    Steadman's heat index (simplified Rothfusz regression).
    Only meaningful above 27°C / 80°F.
    Returns heat index in Celsius.
    """
    t = celsius_to_fahrenheit(temp_celsius)
    rh = humidity_percent
    hi = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t * t
        - 0.05481717 * rh * rh
        + 0.00122874 * t * t * rh
        + 0.00085282 * t * rh * rh
        - 0.00000199 * t * t * rh * rh
    )
    # Convert back to Celsius
    return round((hi - 32) * 5 / 9, 2)


def enrich_observation(obs: WeatherObservation) -> dict:
    """
    Return the observation as a dict enriched with derived fields.
    The original model is not mutated.
    """
    data = obs.model_dump()

    data["temperature_fahrenheit"] = round(celsius_to_fahrenheit(obs.temperature_celsius), 2)
    data["feels_like_fahrenheit"] = round(celsius_to_fahrenheit(obs.feels_like_celsius), 2)
    data["wind_speed_kmh"] = round(ms_to_kmh(obs.wind_speed_ms), 2)
    data["wind_speed_mph"] = round(ms_to_mph(obs.wind_speed_ms), 2)
    data["pressure_inhg"] = round(hpa_to_inhg(obs.pressure_hpa), 4)
    data["dew_point_celsius"] = compute_dew_point(
        obs.temperature_celsius, obs.humidity_percent
    )
    if obs.wind_direction_degrees is not None:
        data["wind_direction_cardinal"] = wind_degrees_to_cardinal(
            obs.wind_direction_degrees
        )
    if obs.temperature_celsius >= 27:
        data["heat_index_celsius"] = compute_heat_index(
            obs.temperature_celsius, obs.humidity_percent
        )

    return data
