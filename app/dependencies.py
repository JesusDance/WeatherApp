from typing import Annotated

from fastapi.params import Depends
from httpx import AsyncClient
from redis.asyncio import Redis

from app.cache.redis_client import get_redis_client
from app.client import get_client
from app.config import Settings, get_settings_from_lifespan


CLIENT_DEP = Annotated[AsyncClient, Depends(get_client)]
REDIS_DEP = Annotated[Redis, Depends(get_redis_client)]
SettingsDep = Annotated[Settings, Depends(get_settings_from_lifespan)]