import json
from typing import Optional, Any

import structlog
from redis.asyncio import Redis

from src.application.interfaces import AbstractCacheService

class RedisCacheService(AbstractCacheService):
    """Универсальный сервис кэширования для любых сущностей."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.logger = structlog.get_logger(__name__)
    
    async def save(self, key: str, data: Any, ttl: int = 300):
        """Сохранить данные в кэш."""
        if isinstance(data, str):
            json_data = data
        else:
            json_data = json.dumps(data)
        await self.redis.set(key, json_data, ex=ttl)
    
    async def load(self, key: str) -> Optional[Any]:
        """Загрузить данные из кэша."""
        data = await self.redis.get(key)
        if not data:
            return None
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            self.logger.warning("Ошибка парсинга JSON из кэша", key=key)
            return None
    
    async def invalidate(self, key: str):
        """Очистить кэш."""
        await self.redis.delete(key)