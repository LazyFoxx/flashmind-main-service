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
                    stability=None,
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
                stability=card._fsrs_card.stability,
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

    async def get_due_cards(
        self,
        deck_id: UUID,
        due_before: datetime,
        limit: Optional[int] = None,
    ) -> list[Card]:
        query = (
            select(CardModel)
            .where(CardModel.deck_id == deck_id)
            .where(CardModel.next_due <= due_before)
            .order_by(CardModel.next_due.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        card_models = result.scalars().all()

        return [card_model.to_entity() for card_model in card_models]
    

    async def get_total_due_cards_by_deck_ids(
        self,
        deck_ids: List[UUID],
        due_before: datetime,
    ) -> List[Tuple[UUID, int]]:
        """
        Возвращает список кортежей (deck_id, total_due_cards) для указанных колод.
        total_due_cards — это количество карт, у которых next_due <= due_before.
        """

        query = (
            select(
                CardModel.deck_id,
                func.count(
                    CardModel.id
                 ).label("due_count"),
             )
             .where(CardModel.deck_id.in_(deck_ids))
             .where(CardModel.next_due.isnot(None))
             .where(CardModel.next_due <= due_before)
             .group_by(CardModel.deck_id)
         )

        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [(row.deck_id, row.due_count) for row in rows]
