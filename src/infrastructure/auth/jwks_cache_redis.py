import json

from authlib.jose import JsonWebKey
from redis.asyncio import Redis

from src.application.interfaces import JWKSCache


class RedisJWKSCache(JWKSCache):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, kid: str) -> JsonWebKey | None:
        raw = await self.redis.get(f"jwks:{kid}")
        if raw:
            return JsonWebKey.import_key(json.loads(raw))
        return None

    async def set(self, kid: str, key: JsonWebKey, ttl: int) -> None:
        await self.redis.setex(
            f"jwks:{kid}",
            ttl,
            json.dumps(key.as_dict()),
        )
