import httpx
from fastapi import status, HTTPException, Request
from httpx import AsyncClient

from app.config import settings
from app.logger import logger


def get_client(request: Request) -> AsyncClient:
    return request.app.state.httpx_client


class WeatherClient:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def fetch_temp_from_openweather_api(self, city: str) -> tuple[float, float]:
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




