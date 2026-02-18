from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractCardRepository, Card
from src.infrastructure.db.models import CardModel


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

    # async def list_by_deck(self, deck_id: UUID) -> List[Card]:
    #     """Получить все карточки колоды.

    #     Args:
    #         deck_id: UUID колоды

    #     Returns:
    #         Список объектов Card
    #     """
    #     ...

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
