from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .cloud_deck import CloudDeck


class AbstractCloudDeckRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self, deck_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[CloudDeck]:
        """Получить облачную колоду по её уникальному идентификатору..

        Args:
            deck_id: UUID колоды

        Returns:
            Объект CloudDeck, если найден, иначе None
        """
        ...

    @abstractmethod
    async def add(self, deck: CloudDeck) -> None:
        """Добавить новую колоду в хранилище.

        Колода должна быть новой (без ID или с временным).
        После добавления у колоды должен появиться валидный ID из БД.

        Args:
            deck: Объект CloudDeck

        Raises:
            IntegrityError: если имя колоды уже занято для пользователя
        """
        ...
    
    @abstractmethod
    async def autoincr_downloaded(self, deck_id: UUID) -> None:
        """Добавляет скачивание к downloaded.

        Args:
            deck_id: UUID колоды

        Returns:
            None
        """
        ...
    
    @abstractmethod
    async def update_last_synced_at(self, cloud_deck_id: UUID) -> None:
        """
        Устанавливает текущее время в поле last_synced_at для указанной колоды.
        
        Args:
            deck_id: UUID колоды
        """
        ...
    
    @abstractmethod
    async def get_last_synced_at(self, cloud_deck_id: UUID) -> Optional[datetime]:
        """
        Получает время последней синхронизации для указанной колоды.
        
        Args:
            deck_id: UUID колоды
            
        Returns:
            datetime или None
        """
        ...