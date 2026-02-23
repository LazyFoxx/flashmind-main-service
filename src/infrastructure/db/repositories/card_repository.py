from datetime import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractCardRepository, Card
from src.infrastructure.db.models import CardModel, DeckModel, UserProfileModel


class SQlAlchemyCardRepository(AbstractCardRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, card_id: UUID) -> Optional[Card]:
        stmt = select(CardModel).where(CardModel.id == card_id)
        result = await self.session.execute(stmt)
        card_model = result.scalar_one_or_none()
        return card_model.to_entity() if card_model else None

    async def get_by_front(
        self, front: str, deck_id: Optional[UUID] = None
    ) -> Optional[Card]:
        stmt = select(CardModel).where(CardModel.front == front)

        if deck_id is not None:
            stmt = stmt.where(CardModel.deck_id == deck_id)

        result = await self.session.execute(stmt)
        card_model = result.scalar_one_or_none()
        return card_model.to_entity() if card_model else None

    async def add(self, card: Card, deck_id: UUID) -> None:
        card_model = CardModel.from_domain(card)
        self.session.add(card_model)

    async def update(self, card: Card) -> None:

        if card._fsrs_card is None:
            stmt = (
                update(CardModel)
                .where(CardModel.id == card.id)
                .values(
                    front=card.front,
                    back=card.back,
                    fsrs_state=None,
                    next_due=None,
                    difficulty=None,
                )
            )
            return None

        stmt = (
            update(CardModel)
            .where(CardModel.id == card.id)
            .values(
                front=card.front,
                back=card.back,
                fsrs_state=card._fsrs_card.to_json(),
                next_due=card._fsrs_card.due,
                difficulty=card._fsrs_card.difficulty,
                in_learning=card.in_learning,
            )
        )
        await self.session.execute(stmt)

    async def delete(self, card_id: UUID) -> None:
        await self.session.execute(delete(CardModel).where(CardModel.id == card_id))

    async def get_all_light_by_user_and_deck(
        self,
        user_id: UUID,
        deck_id: Optional[UUID] = None,
        offset: Optional[int] = None,  # None = все
        limit: Optional[int] = None,  # None = все
    ) -> List[tuple[UUID, UUID, str]]:

        query = select(
            CardModel.id,
            CardModel.deck_id,
            CardModel.front,
        )

        # Если есть deck_id, фильтруем по нему
        if deck_id:
            query = query.where(CardModel.deck_id == deck_id)

        # Если deck_id не передан, фильтруем по пользователю через колоды
        else:
            query = (
                query.join(
                    DeckModel
                )  # Присоединим DeckModel, чтобы фильтровать по колодам пользователя
                .join(
                    UserProfileModel
                )  # Присоединим UserProfileModel, чтобы фильтровать по user_id
                .where(DeckModel.user_id == user_id)
            )

        if limit is not None:
            query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        rows = result.fetchall()

        # Преобразуем результат в список кортежей
        cards = [(row[0], row[1], row[2]) for row in rows]
        return cards

    async def get_total_cards_by_deck_id(self, deck_id: UUID) -> int:
        query = select(func.count(CardModel.id)).where(CardModel.deck_id == deck_id)

        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def get_total_cards_by_deck_ids(
        self,
        deck_ids: List[UUID],
    ) -> List[Tuple[UUID, int]]:

        query = (
            select(
                DeckModel.id.label("deck_id"),
                func.count(CardModel.id).label("card_count"),
            )
            .outerjoin(CardModel, DeckModel.id == CardModel.deck_id)
            .group_by(DeckModel.id)
        )

        query = query.where(DeckModel.id.in_(deck_ids))
        result = await self.session.execute(query)
        rows = result.fetchall()
        return [(row.deck_id, row.card_count) for row in rows]

    async def get_by_deck_id(
        self,
        deck_id: UUID,
        in_learning: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Card]:

        # Базовый запрос, выбираем все карточки в deck
        query = select(CardModel).where(CardModel.deck_id == deck_id)

        # Фильтрация по статусу обучения
        if in_learning is not None:
            query = query.where(CardModel.in_learning == in_learning)

        # сортировка по дате создания
        query = query.order_by(desc(CardModel.created_at))

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        card_models = result.scalars().all()

        return [card_model.to_entity() for card_model in card_models]
        ...

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
