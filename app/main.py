from collections.abc import AsyncGenerator

from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import Any
from httpx import AsyncClient
from redis.asyncio import Redis

from app.config import settings
from app.routers.weather import router as weather_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[Any, None]:
    try:
        app.state.httpx_client = AsyncClient(http2=True)
        app.state.redis_client = Redis.from_url(
            url=settings.REDIS_URL,
            auto_close_connection_pool=True
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
