import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

from app.cache.redis_client import get_redis_client
from app.config import get_test_settings
from app.main import app
from tests.fake_redis import override_redis_client


@pytest_asyncio.fixture
async def test_client():
    #os.environ["CONFIG_TYPE"] = "app.config.TestSettings"
    app.dependency_overrides[get_redis_client] = override_redis_client
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            http2=True,
            timeout=10,
            base_url="http://test",
            transport=ASGITransport(app=manager.app),
            follow_redirects=True,
        ) as client:
            app.state.settings = get_test_settings()
            yield client
    app.dependency_overrides.clear()