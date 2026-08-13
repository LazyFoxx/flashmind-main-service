from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID

from .cloud_card import CloudCardTemplate


class AbstractCloudCardTemplateRepository(ABC):
    @abstractmethod
    async def add(self, card: CloudCardTemplate, deck_id: UUID) -> None:
        """Добавить новую карточку.

        Args:
            card: Объект Card с валидными данными
            deck_id: UUID колоды, к которой привязать

        """
        ...
    
    @abstractmethod
    async def get_by_id(self, card_id: UUID) -> Optional[CloudCardTemplate]:
        """Получить карточку по её уникальному идентификатору.

        Args:
            card_id: UUID карточки

        Returns:
            Объект CloudCardTemplate, если найден, иначе None
        """
        ...

    @abstractmethod
    async def delete(self, card_id: UUID) -> None:
        """Удалить карточку.

        Args:
            card_id: UUID карточки
        """
        ...
    
    @abstractmethod
    async def update(self, card: CloudCardTemplate) -> None:
        """Обновить существующую карточку.

        Args:
            card: Объект CloudCardTemplate

        """
        ...

    @abstractmethod
    async def get_by_deck_id(
        self,
        cloud_deck_id: UUID,
    ) -> List[CloudCardTemplate]:
        """Получить список CloudCardTemplate по deck_id.

        Args:
            cloud_deck_id: UUID колоды

        Returns:
            List[CloudCardTemplate]
        """
        ...
    
    async def get_total_cards_count(self, cloud_deck_id: UUID) -> int:
        """Возвращает общее количество карточек в колоде.

        Args:
            cloud_deck_id: UUID колоды

        Returns:
            int
        """
        ...