from typing import Annotated

from fastapi.params import Depends
from httpx import AsyncClient

from app.client import get_client

CLIENT = Annotated[AsyncClient, Depends(get_client)]
