import httpx
from fastapi import status, HTTPException, Request
from httpx import AsyncClient

from app.config import settings
from app.logger import logger


def get_client(request: Request) -> AsyncClient:
    return request.app.state.httpx_client


class WeatherClient:
    def __init__(
            self,
            client: AsyncClient,
            url: str = settings.URL,
            forecast_url: str = settings.FORECAST_URL,
            api_key: str = settings.API_KEY
    ):
        self.client = client
        self.url = url
        self.forecast_url = forecast_url
        self.api_key = api_key


    async def fetch_weather(self, city: str) -> tuple[float, float]:
        logger.info("Fetching temp from external API", extra={"city": city})
        try:
            response = await self.client.get(
                self.url,
                params={
                    "q": city,
                    "lang": "en",
                    "units": "metric",
                    "appid": self.api_key,
                },
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            temp, wind = data["main"].get("temp", 0), data["wind"].get("speed", 0)
            return temp, wind

        except httpx.ConnectError:
            logger.warning("Cannot connect to openweather")
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Cannot connect to openweather")

        except httpx.TimeoutException:
            logger.warning("External APi timeout")
            raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "External APi timeout")

        except httpx.HTTPStatusError as exc:
            response_status = exc.response.status_code
            if response_status == 404:
                logger.warning("City not found")
                raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")
            if response_status == 401:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid OpenWeather API key")
            if response_status == 429:
                raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests")

            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Weather service doesn't response")


    async def fetch_weather_for_five_days(self, city: str) -> list[dict]:
        logger.info("Fetch weather forecast", extra={"city": city})
        try:
            response = await self.client.get(
                self.forecast_url,
                params={
                    "q": city,
                    "lang": "en",
                    "units": "metric",
                    "appid": self.api_key,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            result = [
                {
                    "temp_min": data["list"][0]["main"].get("temp_min"),
                    "temp_max": data["list"][0]["main"].get("temp_max"),
                    "feels_like": data["list"][0]["main"].get("feels_like"),
                    "dt_txt": data["list"][0]["dt_txt"],
                },
                    {
                    "temp_min": data["list"][8]["main"].get("temp_min"),
                    "temp_max": data["list"][8]["main"].get("temp_max"),
                    "feels_like": data["list"][8]["main"].get("feels_like"),
                    "dt_txt": data["list"][8]["dt_txt"],
                },
                {
                    "temp_min": data["list"][16]["main"].get("temp_min"),
                    "temp_max": data["list"][16]["main"].get("temp_max"),
                    "feels_like": data["list"][16]["main"].get("feels_like"),
                    "dt_txt": data["list"][16]["dt_txt"],
                },
                {
                    "temp_min": data["list"][24]["main"].get("temp_min"),
                    "temp_max": data["list"][24]["main"].get("temp_max"),
                    "feels_like": data["list"][24]["main"].get("feels_like"),
                    "dt_txt": data["list"][24]["dt_txt"],
                },
                {
                    "temp_min": data["list"][32]["main"].get("temp_min"),
                    "temp_max": data["list"][32]["main"].get("temp_max"),
                    "feels_like": data["list"][32]["main"].get("feels_like"),
                    "dt_txt": data["list"][32]["dt_txt"],
                },

            ]
            return result


        except httpx.ConnectError:
            logger.warning("Cannot connect to openweather")
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Cannot connect to openweather")

        except httpx.TimeoutException:
            logger.warning("External APi timeout")
            raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "External APi timeout")

        except httpx.HTTPStatusError as exc:
            response_status = exc.response.status_code
            if response_status == 404:
                logger.warning("City not found")
                raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")
            if response_status == 401:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid OpenWeather API key")
            if response_status == 429:
                raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests")

            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Weather service doesn't response")