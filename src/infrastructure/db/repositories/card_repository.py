from datetime import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy import delete, func, select, update
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
                in_learning=True,
            )
        )
        await self.session.execute(stmt)

    async def delete(self, card_id: UUID) -> None:
        await self.session.execute(delete(CardModel).where(CardModel.id == card_id))

        ...

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

    async def get_total_cards_by_deck(
        self,
        deck_id: Optional[UUID] = None,
        list_decks_id: Optional[List[UUID]] = None,
    ) -> Union[int, List[Tuple[UUID, int]]]:

        query = select(
            CardModel.deck_id, func.count(CardModel.id).label("card_count")
        ).group_by(CardModel.deck_id)

        # Если передан один deck_id, фильтруем по этому deck_id
        if deck_id:
            query = query.where(CardModel.deck_id == deck_id)
            result = await self.session.execute(query)
            total_cards = result.scalar()
            return total_cards or 0

        # Если передан список колод
        elif list_decks_id:
            query = query.where(CardModel.deck_id.in_(list_decks_id))
            result = await self.session.execute(query)
            total_cards = result.fetchall()  # получаем список (deck_id, count)
            return [(row[0], row[1]) for row in total_cards]

        result = await self.session.execute(query)
        total_cards = result.scalar()
        return total_cards or 0

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
