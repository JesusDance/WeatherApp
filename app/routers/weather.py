from typing import Annotated

from fastapi import APIRouter
from fastapi import status
from fastapi.params import Query
from starlette.requests import Request

from app.cache.keys import weather_key, weather_forecast
from app.cache.redis_client import RedisClient
from app.client import WeatherClient
from app.dependencies import CLIENT_DEP, REDIS_DEP
from app.schemas import City, ReadWeatherData, ReadWeatherFiveDays, ReadDay

router = APIRouter(prefix="/weather", tags=["weather"])

CITY_QUERY = Annotated[City, Query()]


@router.get("/", status_code=status.HTTP_200_OK, response_model=ReadWeatherData)
async def get_weather(
        client: CLIENT_DEP,
        redis: REDIS_DEP,
        request: Request,
        city: CITY_QUERY,
) -> ReadWeatherData:
    redis_client = RedisClient(redis)
    cache = await redis_client.get_cache(weather_key(city.name))
    if cache is not None:
        return ReadWeatherData.model_validate(cache)
    await redis_client.rate_limit_by_ip(request)

    weather_client = WeatherClient(client)
    temp, wind = await weather_client.fetch_weather(city.name)
    result = {
        "city": city.name,
        "temp": temp,
        "wind": wind,
    }
    await redis_client.set_cache(weather_key(city.name), result)
    return ReadWeatherData.model_validate(result)


@router.get("/forecast", status_code=status.HTTP_200_OK, response_model=ReadWeatherFiveDays)
async def get_weather_forecast(
        client: CLIENT_DEP,
        redis: REDIS_DEP,
        request: Request,
        city: CITY_QUERY,
) -> ReadWeatherFiveDays:
    redis_client = RedisClient(redis)
    cache = await redis_client.get_cache(weather_forecast(city.name))
    if cache is not None:
        return ReadWeatherFiveDays.model_validate(cache)
    await redis_client.rate_limit_by_ip(request)

    weather_client = WeatherClient(client)
    result = await weather_client.fetch_weather_for_five_days(city.name)
    weather_for_read = [ReadDay.model_validate(day).model_dump(mode="json") for day in result]
    result_for_read = {
        "city": city.name,
        "days": weather_for_read,
    }
    await redis_client.set_cache(weather_forecast(city.name), result_for_read)
    return ReadWeatherFiveDays.model_validate(result_for_read)
