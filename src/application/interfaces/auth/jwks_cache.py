from abc import ABC, abstractmethod
from typing import Any, Mapping


class JWKSCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Mapping[str, Any] | None:
        """Возвращает кешированный ключ или None если не нашел."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, kid: str, key: str, ttl: int) -> None:
        """Сохраняет jwks в кэш."""
        raise NotImplementedError
