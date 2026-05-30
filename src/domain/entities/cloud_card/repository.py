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
