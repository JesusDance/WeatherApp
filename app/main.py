from fastapi import FastAPI
from contextlib import asynccontextmanager

from httpx import AsyncClient
from app.routers.weather import router as weather_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.httpx_client = AsyncClient(http2=True)
    yield
    await app.state.httpx_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(weather_router)


@app.get("/")
def health():
    return {"detail": "Hello from Back End!"}
