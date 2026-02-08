from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from src.core.settings import RedisSettings
from src.infrastructure.redis.client import create_redis_client


class RedisProvider(Provider):
    # Основной клиент — просто Redis (без AsyncGenerator)
    @provide(scope=Scope.APP)
    async def redis_client(self, redis_settings: RedisSettings) -> Redis:
        return await create_redis_client(redis_settings)

    # Отдельный провайдер для закрытия при shutdown приложения
    @provide(scope=Scope.APP, provides=AsyncGenerator[None, None])
    async def redis_shutdown(self, redis_client: Redis) -> AsyncGenerator[None, None]:
        try:
            yield
        finally:
            await redis_client.aclose()
