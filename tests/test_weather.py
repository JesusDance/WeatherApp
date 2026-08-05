import pytest
import httpx
from pytest_httpx import HTTPXMock


forecast = [
    {
        "main": {
        "temp": 28.73,
        "feels_like": 31.81,
        "temp_min": 27.81,
        "temp_max": 28.73,
        },
        "dt_txt": "2026-08-04 12:00:00",
        "wind": {"speed": 2.87},
    }
    for _ in range(40)
]


@pytest.mark.asyncio
async def test_get_weather(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/forecast?"
            "q=Kiev&lang=en&units=metric&appid=test_key",
        http_version="HTTP/2.0",
        status_code=200,
        is_optional=True,
        json={
            "city": {"name": "Kyiv"},
            "list": forecast,
        },
    )

    response = await test_client.get('/weather/forecast', params={"name": "Kiev"})

    json_response = response.json()
    assert response.status_code == 200
    assert json_response["city"] == "Kiev"
    assert json_response["days"][0]["temp_min"] == 27.81


@pytest.mark.asyncio
async def test_httpx_url(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=httpx.URL("https://api.openweathermap.org/data/2.5/weather"),
        http_version="HTTP/2.0",
        status_code=200,
        is_optional=True,
        json={
            "main": {"temp": 25.5},
            "wind": {"speed": 2.1},
        },
        match_params={
            "q": "Kiev",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )

    response = await test_client.get('/weather/', params={"name": "Kiev"})
    assert response.status_code == 200
    assert response.json()["city"] == "Kiev"
    assert response.json()["temp"] == 25.5


@pytest.mark.asyncio
async def test_unauthorised(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        http_version="HTTP/2.0",
        status_code=401,
        match_params={
            "q": "Odesa",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    response = await test_client.get("/weather/", params={"name": "Odesa"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid OpenWeather API key"


@pytest.mark.asyncio
async def test_city_not_found(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        http_version="HTTP/2.0",
        status_code=404,
        match_params={
            "q": "Odesa",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    response = await test_client.get("/weather/", params={"name": "Odesa"})
    assert response.status_code == 404
    assert response.json()["detail"] == "City not found"


@pytest.mark.asyncio
async def test_service_doesnt_response(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(
        exception=httpx.ConnectError("Cannot connect to openweather"),
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        match_params={
            "q": "Odesa",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    response = await test_client.get("/weather/", params={"name": "Odesa"})
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_connect_failed(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        http_version="HTTP/2.0",
        status_code=502,
        match_params={
            "q": "Odesa",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    response = await test_client.get("/weather/", params={"name": "Odesa"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Weather service doesn't response"


@pytest.mark.asyncio
async def test_timeout(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_exception(
        exception=httpx.TimeoutException("External APi timeout"),
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        match_params={
            "q": "Odesa",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    response = await test_client.get("/weather/", params={"name": "Odesa"})
    assert response.status_code == 504


@pytest.mark.asyncio
async def test_requests_limit(test_client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        http_version="HTTP/2.0",
        status_code=200,
        json={
            "main": {"temp": 25.5},
            "wind": {"speed": 2.1},
        },
        match_params={
            "q": "Lviv",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        http_version="HTTP/2.0",
        status_code=200,
        json={
            "main": {"temp": 25.5},
            "wind": {"speed": 2.1},
        },
        match_params={
            "q": "Kiev",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )
    httpx_mock.add_response(
        url="https://api.openweathermap.org/data/2.5/weather",
        is_optional=True,
        http_version="HTTP/2.0",
        status_code=429,
        match_params={
            "q": "Poltava",
            "lang": "en",
            "units": "metric",
            "appid": "test_key",
        },
    )

    response = await test_client.get("/weather/", params={"name": "Lviv"})
    assert response.status_code == 200

    response = await test_client.get("/weather/", params={"name": "Kiev"})
    assert response.status_code == 200

    response = await test_client.get("/weather/", params={"name": "Poltava"})
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"

