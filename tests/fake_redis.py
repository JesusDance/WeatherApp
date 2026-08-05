class FakeRedis:
    def __init__(self):
        self.storage = {}


    async def get(self, key: str) -> dict:
        return self.storage.get(key)

    async def set(self, name: str, value: dict, ex=None) -> None:
        self.storage[name] = value

    async def delete(self, key: str) -> None:
        self.storage.pop(key)

    async def expire(self, name: str, time: int = 60) -> bool:
        return True

    async def incr(self, key: str) -> int:
        return self.storage.get(key, 0) + 1


fake_redis = FakeRedis()

def override_redis_client() -> FakeRedis:
    return fake_redis