from datetime import datetime

from pydantic import BaseModel, Field


class City(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class ReadWeatherData(BaseModel):
    city: str
    temp: float
    wind: float


class ReadDay(BaseModel):
    temp_min: float
    temp_max: float
    feels_like: float
    dt_txt: datetime


class ReadWeatherFiveDays(BaseModel):
    city: str
    days: list[ReadDay]