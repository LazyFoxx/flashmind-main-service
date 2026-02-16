from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .deck import Deck


class AbstractDeckRepository(ABC):
    @abstractmethod
    async def get_by_id(self, deck_id: UUID) -> Optional[Deck]:
        """Получить колоду по её уникальному идентификатору.

        Args:
            deck_id: UUID колоды

        Returns:
            Объект Deck, если найден, иначе None
        """
        ...

    @abstractmethod
    async def add(self, deck: Deck) -> None:
        """Добавить новую колоду в хранилище.

        Колода должна быть новой (без ID или с временным).
        После добавления у колоды должен появиться валидный ID из БД.
        Карточки (card_ids) сохраняются отдельно через CardRepository.

        Args:
            deck: Объект Deck с валидными данными

        Raises:
            IntegrityError: если имя колоды уже занято для пользователя
        """
        ...

    @abstractmethod
    async def update(self, deck: Deck) -> None:
        """Обновить существующую колоду.

        Обновляются поля name, description
        Карточки сохраняются отдельно.

        Args:
            deck: Объект Deck

        Raises:
            NotFoundError: если колода не существует
        """
        ...

    # @abstractmethod
    # async def delete(self, deck_id: UUID) -> None:
    #     """Удалить колоду и все её карточки (каскадное удаление).

    #     Args:
    #         deck_id: UUID колоды
    #     """
    #     ...

    # @abstractmethod
    # async def list_by_user(self, user_id: UUID) -> List[Deck]:
    #     """Получить список всех колод пользователя.

    #     Args:
    #         user_id: UUID пользователя

    #     Returns:
    #         Список объектов Deck
    #     """
    #     ...
