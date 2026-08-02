from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID

from .card import Card


class AbstractCardRepository(ABC):
    @abstractmethod
    async def get_by_id(self, card_id: UUID) -> Optional[Card]:
        """Получить карточку по её уникальному идентификатору.

        Args:
            card_id: UUID карточки

        Returns:
            Объект Card, если найден, иначе None
        """
        ...

    @abstractmethod
    async def get_by_front(
        self, front: str, deck_id: Optional[UUID] = None
    ) -> Optional[Card]:
        """
        Находит карточку по лицевой стороне и (опционально) по владельцу.

        Args:
            front: точное название карточки
            user_id: если передан — фильтруем только колоды этого пользователя

        Returns:
            Card или None, если ничего не найдено
        """
        ...

    @abstractmethod
    async def add(self, card: Card) -> None:
        """Добавить новую карточку в хранилище и привязать к колоде.

        Карточка должна быть новой (без ID или с временным).
        После добавления у карточки должен появиться валидный ID из БД.

        Args:
            card: Объект Card с валидными данными

        Raises:
            IntegrityError: если фронт/бэк пустой или колода не существует
        """
        ...

    @abstractmethod
    async def update(self, card: Card) -> None:
        """Обновить существующую карточку (включая FSRS-состояние после review).

        Args:
            card: Объект Card (новая immutable версия после review)

        Raises:
            NotFoundError: если карточка не существует
        """
        ...

    @abstractmethod
    async def delete(self, card_id: UUID) -> None:
        """Удалить карточку.

        Также нужно удалить card_id из Deck (через событие или DeckRepository).

        Args:
            card_id: UUID карточки
        """
        ...

    @abstractmethod
    async def get_all_light_by_user_and_deck(
        self,
        user_id: UUID,
        desk: True,
        deck_id: Optional[UUID] = None,
        offset: Optional[int] = None,  # None = все
        limit: Optional[int] = None,  # None = все
        created_at: Optional[bool] = None,
        difficulty: Optional[bool] = None,
        stability: Optional[bool] = None,
        

    ) -> List[tuple[UUID, UUID, str, float, float]]:
        """
        Выводит список всех карточек пользователя без обратной стороны.
        Если передан параметр фильтрации deck_id - то выводит карточки по колоде пользователя.
        Если offset и limit переданы, то производится вывод с пагинацией.

        Args:
            user_id: ID пользователя.
            deck_id: ID колоды (если передан, то выводятся карточки по этой колоде).
            offset: Если передан, то пропускает указанное количество карточек.
            limit: Если передан, ограничивает количество возвращаемых карточек.

        Returns:
            List[light_cards]: Список карточек.
        """

    @abstractmethod
    async def get_total_cards_by_deck_id(self, deck_id: UUID) -> int:
        """возвращает количество карточек в колоде как int.

        Args:
            deck_id (UUID): _description_

        Returns:
            int: количество карточек в колоде
        """

    @abstractmethod
    async def get_total_cards_by_deck_ids(
        self,
        deck_ids: List[UUID],
    ) -> List[Tuple[UUID, int]]:
        """
        возвращает список с количеством карточек для каждой колоды:
        [(deck_id, количество карточек)].

        Аргументы:
            deck_ids: Список ID колод (по умолчанию None)

        Возвращает:
            list: [(deck_id, total_cards)]
        """

    @abstractmethod
    async def get_by_deck_id(
    self,
    deck_id: UUID,
    in_learning: Optional[bool] = None,
    limit: Optional[int] = None,
    include_deleted: bool = False,    # ← ДОБАВЛЕН
) -> List[Card]:
     """Получить список Card по id Deck.

     Args:
         deck_id: UUID конкретной колоды
         in_learning:
              - True   → только карточки в обучении (in_learning=True)
              - False → только новые (in_learning=False)
              - None   → все карточки
         limit: Максимальное количество возвращаемых карточек (None = без ограничения)
         include_deleted:
              - True   → включать удалённые карточки
              - False  → только не удалённые (по умолчанию)

     Returns:
         List[Card]   # domain entities
      """
     ...


    @abstractmethod
    async def get_due_cards(
        self,
        deck_id: UUID,
        due_before: datetime,
        limit: Optional[int] = None,
    ) -> List[Card]:
        """Получить карточки, которые пора повторять.

        Args:
            deck_id: UUID конкретной колоды (если None — все колоды пользователя)
            due_before: Момент времени, относительно которого проверяется due
            limit: Максимальное количество возвращаемых карточек
                 (None = без ограничения)

        Returns:
            Список объектов Card, готовых к повторению, отсортированных по due (от более ранних)

        Raises:
            ValueError: если deck_id и user_id оба None
        """
        
    @abstractmethod
    async def get_total_due_cards_by_deck_ids(
        self,
        deck_ids: List[UUID],
        due_before: datetime,
    ) -> List[Tuple[UUID, int]]:
        """
        возвращает список с количеством карточек к повтору сегодня для каждой колоды:
        [(deck_id, количество карточек)].

        Аргументы:
            deck_ids: Список ID колод (по умолчанию None)

        Возвращает:
            list: [(deck_id, total_cards)]
        """
    
    @abstractmethod
    async def delete_orphan_deleted_cards(self) -> int:
        """Удалить все карточки, где is_deleted=True И card_template_id=None.
        
        Returns:
            Количество удалённых карточек.
        """
        ...

