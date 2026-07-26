from pydantic import BaseModel, Field


class City(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class ReadWeatherData(BaseModel):
    city: str
    temp: float
    wind: float
