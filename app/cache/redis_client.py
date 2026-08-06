import json
from typing import Any

from fastapi import HTTPException, status
from redis import RedisError
from redis.asyncio import Redis
from starlette.requests import Request

from app.config import get_settings_from_lifespan, Settings
from app.logger import logger


def get_redis_client(r: Request) -> Redis:
    return r.app.state.redis_client


class RedisClient:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client


    async def get_cache(self, key: str) -> dict[str, Any] | None:
        try:
            value = await self.redis_client.get(key)
            if value is None:  # Якщо значення ще не існує, щоб json не конвертував None
                return None
            return json.loads(value)
        except RedisError:
            logger.warning("Failed to read weather cache", extra={"key": key})
            return None


    async def set_cache(self, key: str, value: dict, settings: Settings) -> None:
        try:
            await self.redis_client.set(
                name=key, value=json.dumps(value), ex=settings.CACHE_TTL_SECONDS
            )
        except RedisError:
            logger.warning("Failed to write weather cache", extra={"key": key})


    async def delete(self, key: str) -> None:
        try:
            await self.redis_client.delete(key)
        except RedisError:
            logger.warning("Failed to invalidate", extra={"key": key})

    async def delete_pattern(self):
        ...

    async def rate_limit_by_ip(
            self,
            r: Request,
            settings: Settings,
    ):
        credentials = HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests"
        )
        ip = r.client.host

        key = f"request:{ip}"
        requests = await self.redis_client.incr(key)
        if requests == 1:
            await self.redis_client.expire(name=key, time=settings.CACHE_EXPIRE_SECONDS)
        if requests > settings.REQUESTS_LIMIT:
            raise credentials