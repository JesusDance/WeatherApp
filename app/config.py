from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

from starlette.requests import Request


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    URL: str = f"https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL: str = f"https://api.openweathermap.org/data/2.5/forecast"
    API_KEY: str

    REDIS_URL: str = "redis://localhost:6379/0"
    REQUESTS_LIMIT: int = 10
    CACHE_EXPIRE_SECONDS: int = 60
    CACHE_TTL_SECONDS: int = 600

    START: int = 0
    STOP: int = 5
    STEP_EVERY_DAY: int = 8


def get_test_settings() -> Settings:
    return Settings(API_KEY="test_key")


#Ініціалізуємо об'єкт налаштувань в лайфспенє
@lru_cache
def get_settings() -> Settings:
    return Settings()

print(get_settings.cache_info())
#Отримуємо створений об'єкт налаштувань з лайфспена
def get_settings_from_lifespan(request: Request) -> Settings:
    return request.app.state.settings