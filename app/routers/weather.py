from typing import Annotated

from fastapi import APIRouter
from fastapi import status
from fastapi.params import Query

from app.client import WeatherClient
from app.dependencies import CLIENT
from app.schemas import City, ReadWeatherData

router = APIRouter(prefix="/weather", tags=["weather"])

CITY = Annotated[City, Query()]


@router.get("/", status_code=status.HTTP_200_OK, response_model=ReadWeatherData)
async def get_temperature(client: CLIENT, city: CITY) -> ReadWeatherData:
    weather_client = WeatherClient(client)
    temp, wind = await weather_client.fetch_temp_from_openweather_api(city.name)
    result = {
        "city": city.name,
        "temp": temp,
        "wind": wind,
    }
    return ReadWeatherData.model_validate(result)
