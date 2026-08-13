from abc import ABC, abstractmethod
from typing import Optional, List


class AbstractCacheService(ABC):
    """Универсальный сервис кэширования для любых сущностей."""
    
    @abstractmethod
    async def save(self, key: str, data: list, ttl: int = 300) -> None:
        """Сохранить список объектов в кэш.
        
        Args:
            key: ключ кэширования
            data: список сериализуемых объектов
            ttl: время жизни в секундах (по умолчанию 300)
        """
        ...
    
    @abstractmethod
    async def load(self, key: str) -> Optional[list]:
        """Загрузить список объектов из кэша.
        
        Args:
            key: ключ кэширования
            
        Returns:
            Список объектов или None, если кэш пуст
        """
        ...
    
    @abstractmethod
    async def invalidate(self, key: str) -> None:
        """Очистить кэш по ключу.
        
        Args:
            key: ключ кэширования
        """
        ...