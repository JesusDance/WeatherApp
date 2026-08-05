import httpx
from fastapi import status, HTTPException, Request
from httpx import AsyncClient

from app.config import Settings
from app.forecast_aggregation import get_min_value, get_max_value, \
    get_average_feels_like_value
from app.logger import logger


def get_client(request: Request) -> AsyncClient:
    return request.app.state.httpx_client


class WeatherClient:
    def __init__(self, client: AsyncClient):
        self.client = client


    async def fetch_weather(
            self,
            city: str,
            settings: Settings,
    ) -> tuple[float, float]:

        logger.info("Fetching temp from external API", extra={"city": city})
        try:
            response = await self.client.get(
                settings.URL,
                params={
                    "q": city,
                    "lang": "en",
                    "units": "metric",
                    "appid": settings.API_KEY,
                },
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            if data:
                temp, wind = data["main"]["temp"], data["wind"]["speed"]
                return temp, wind
            else:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

        except httpx.ConnectError:
            logger.warning("Cannot connect to openweather")
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Cannot connect to openweather"
            )

        except httpx.TimeoutException:
            logger.warning("External APi timeout")
            raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "External APi timeout")

        except httpx.HTTPStatusError as exc:
            response_status = exc.response.status_code
            if response_status == 404:
                logger.warning("City not found")
                raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")
            if response_status == 401:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Invalid OpenWeather API key"
                )
            if response_status == 429:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests"
                )

            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, "Weather service doesn't response"
            )

    async def fetch_weather_for_five_days(
            self,
            city: str,
            settings: Settings,
    ) -> list[dict]:

        logger.info("Fetch weather forecast", extra={"city": city})
        try:
            response = await self.client.get(
                settings.FORECAST_URL,
                params={
                    "q": city,
                    "lang": "en",
                    "units": "metric",
                    "appid": settings.API_KEY,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            temp_min_all = []
            temp_max_all = []
            temp_feels_like = []
            dt_txt_list = []
            end_average = len(data["list"])
            start = settings.START
            for _ in range(start, end_average):
                min_value = data["list"][start]["main"].get("temp_min")
                max_value = data["list"][start]["main"].get("temp_max")
                feels_like = data["list"][start]["main"].get("feels_like")
                dt_txt = data["list"][start]["dt_txt"]
                temp_min_all.append(min_value)
                temp_max_all.append(max_value)
                temp_feels_like.append(feels_like)
                dt_txt_list.append(dt_txt)
                start += 1

            average_min_temp = get_min_value(temp_min_all)
            average_max_temp = get_max_value(temp_max_all)
            average_feels_like = get_average_feels_like_value(temp_feels_like)
            average_dt_txt = get_min_value(dt_txt_list)

            main_result = []
            stop = settings.STOP
            start = settings.START
            for _ in range(stop):
                weather = {
                    "temp_min": average_min_temp[start],
                    "temp_max": average_max_temp[start],
                    "feels_like": average_feels_like[start],
                    "dt_txt": average_dt_txt[start],
                }
                main_result.append(weather)
                start += 1

            return main_result

        except httpx.ConnectError:
            logger.warning("Cannot connect to openweather")
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Cannot connect to openweather"
            )

        except httpx.TimeoutException:
            logger.warning("External APi timeout")
            raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "External APi timeout")

        except httpx.HTTPStatusError as exc:
            response_status = exc.response.status_code
            if response_status == 404:
                logger.warning("City not found")
                raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")
            if response_status == 401:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Invalid OpenWeather API key"
                )
            if response_status == 429:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests"
                )

            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, "Weather service doesn't response"
            )
