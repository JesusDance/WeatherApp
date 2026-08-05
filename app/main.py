from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import Redis

from app.config import get_settings
from app.routers.weather import router as weather_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[Any, None]:
    try:
        app.state.httpx_client = AsyncClient(http2=True)
        app.state.settings = get_settings()
        app.state.redis_client = Redis.from_url(
            url=app.state.settings.REDIS_URL,
            decode_responses=True,
        )
        yield
    finally:
        await app.state.httpx_client.aclose()
        await app.state.redis_client.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(weather_router)


@app.get("/")
def health():
    return {"detail": "Hello from Back End!"}
