from typing import Optional
from app.tools.weather import get_current_weather, get_forecast


def get_current(city: str) -> str:
    """Wrapper around the deterministic tool for current weather."""
    # tools return human-readable strings; this wrapper centralizes error handling and future formatting
    return get_current_weather(city=city)


def get_multi_day_forecast(city: str, days: int = 3) -> str:
    return get_forecast(city=city, days=days)
