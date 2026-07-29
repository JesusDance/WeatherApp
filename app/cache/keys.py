def weather_key(city: str) -> str:
    normalized_city = city.strip().casefold()
    return f"cache_weather:{normalized_city}"


def weather_forecast(city: str) -> str:
    normalized_city = city.strip().casefold()
    return f"cache_weather_five_days:{normalized_city}"