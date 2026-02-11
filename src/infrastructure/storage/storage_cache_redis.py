from redis.asyncio import Redis
from src.application.interfaces import AbstractS3Cache
import structlog

class RedisS3Cache(AbstractS3Cache):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.logger = structlog.get_logger(__name__)

    async def get_url(self, key: str) -> str | None:
        url = await self.redis.get(key)
        if url:
            self.logger.info("Получена ссылка из кэша по ключу", key=key)
            return url
        return None

    async def set_url(self, key: str, url: str, ttl: int) -> None:
        await self.redis.set(
        key,
        url,
        ex=ttl,
        nx=True,
    )
        self.logger.info("Сохранена ссылка в кэш по ключу", key=key)


