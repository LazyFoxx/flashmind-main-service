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
    async def add(self, card: Card, deck_id: UUID) -> None:
        """Добавить новую карточку в хранилище и привязать к колоде.

        Карточка должна быть новой (без ID или с временным).
        После добавления у карточки должен появиться валидный ID из БД.

        Args:
            card: Объект Card с валидными данными
            deck_id: UUID колоды, к которой привязать

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
        deck_id: Optional[UUID] = None,
        offset: Optional[int] = None,  # None = все
        limit: Optional[int] = None,  # None = все
    ) -> List[tuple[UUID, UUID, str]]:
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
    async def get_total_cards_by_deck(
        self,
        deck_id: Optional[UUID] = None,
        list_decks_id: Optional[List[UUID]] = None,
    ) -> Union[int, List[Tuple[UUID, int]]]:
        """
        Если передан deck_id, то возвращает количество карточек в колоде как int.
        Если передан список list_decks_id, то возвращает список с количеством карточек для каждой колоды:
        [(deck_id, количество карточек)].
        Если не передан ни один опциональный аргумент, то возвращает общее количество карточек по всем колодам.

        Аргументы:
            deck_id: ID одной колоды (по умолчанию None, что означает поиск по всем колодам)
            list_decks_id: Список ID колод (по умолчанию None)

        Возвращает:
            total_cards: int — количество карточек в колоде или по всем колодам,
            или список кортежей (deck_id, количество карточек).
        """

    # @abstractmethod
    # async def get_due_cards(
    #     self,
    #     deck_id: Optional[UUID] = None,
    #     user_id: Optional[UUID] = None,
    #     now: Optional[datetime] = None,
    #     limit: Optional[int] = None,
    # ) -> List[Card]:
    #     """Получить карточки, которые пора повторять (due ≤ текущего времени).

    #     Args:
    #         deck_id: UUID конкретной колоды (если None — все колоды пользователя)
    #         user_id: UUID пользователя (обязателен, если deck_id = None)
    #         now: Момент времени, относительно которого проверяется due
    #              (по умолчанию — текущее UTC-время)
    #         limit: Максимальное количество возвращаемых карточек
    #              (None = без ограничения, полезно для пагинации)

    #     Returns:
    #         Список объектов Card, готовых к повторению, отсортированных по due (от более ранних)

    #     Raises:
    #         ValueError: если deck_id и user_id оба None
    #     """
    #     ...
