from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    URL: str = f"https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL: str = f"https://api.openweathermap.org/data/2.5/forecast"
    API_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    REQUESTS_LIMIT: int = 10
    CACHE_EXPIRE_SECONDS: int = 60
    CACHE_TTL_SECONDS: int = 600

settings = Settings()