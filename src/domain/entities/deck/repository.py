from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .deck import Deck


class AbstractDeckRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self, deck_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Deck]:
        """Получить колоду по её уникальному идентификатору и (опционально) по владельцу..

        Args:
            deck_id: UUID колоды
            user_id: если передан — фильтруем только колоды этого пользователя

        Returns:
            Объект Deck, если найден, иначе None
        """
        ...
    
    @abstractmethod
    async def get_by_cloud_deck_id(
        self, cloud_deck_id: UUID, user_id: UUID,
    ) -> Optional[Deck]:
        """Получить колоду по её уникальному идентификатору.

        Args:
            deck_id: UUID колоды

        Returns:
            Объект Deck, если найден, иначе None
        """
        ...


    @abstractmethod
    async def get_by_name(
        self, name: str, user_id: Optional[UUID] = None
    ) -> Optional[Deck]:
        """
        Находит колоду по названию и (опционально) по владельцу.

        Args:
            name: точное название колоды
            user_id: если передан — фильтруем только колоды этого пользователя

        Returns:
            Deck или None, если ничего не найдено
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

        Обновляются поля name, description, desired_retention, maximum_interval, color

        Args:
            deck: Объект Deck

        Raises:
            NotFoundError: если колода не существует
        """
        ...

    @abstractmethod
    async def delete(self, deck_id: UUID, user_id: UUID) -> None:
        """Удалить колоду и все её карточки (каскадное удаление).

        Args:
            deck_id: UUID колоды
            user_id: id владельца колоды
        """
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> List[Deck]:
        """Получить список всех колод пользователя.

        Args:
            user_id: UUID пользователя

        Returns:
            Список объектов Deck
        """
        ...

    @abstractmethod
    async def get_info(
        self,
        deck_id: UUID,
    ) -> dict[str, int]:
        """Получает мета информацюи по колоде.

        Args:
            deck_id: UUID конкретной колоды (если None — все колоды пользователя)

        Returns:
            Словарь со статистикой.

        """
    
    @abstractmethod
    async def update_last_synced_at(self, deck_id: UUID) -> None:
        """
        Устанавливает текущее время в поле last_synced_at для указанной колоды.
        
        Args:
            deck_id: UUID колоды
        """
        ...
    
    @abstractmethod
    async def get_last_synced_at(self, deck_id: UUID) -> Optional[datetime]:
        """
        Получает время последней синхронизации для указанной колоды.
        
        Args:
            deck_id: UUID колоды
            
        Returns:
            datetime или None
        """
        ...

