from abc import ABC, abstractmethod


class AbstractS3Cache(ABC):
    @abstractmethod
    async def get_url(self, key: str) -> str | None:
        """Возвращает кешированную ссылку на фотографию по ключу"""
        raise NotImplementedError

    @abstractmethod
    async def set_url(self, key: str, url: str, ttl: int) -> None:
        """Сохраняет url по ключу в кэш."""
        raise NotImplementedError
