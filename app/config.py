from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    URL: str = f"https://api.openweathermap.org/data/2.5/weather"
    API_KEY: str


settings = Settings()