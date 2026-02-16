from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractDeckRepository, Deck
from src.infrastructure.db.models import DeckModel


class SQlAlchemyDeckRepository(AbstractDeckRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, deck_id: UUID) -> Optional[Deck]:
        stmt = select(DeckModel).where(DeckModel.id == deck_id)
        result = await self.session.execute(stmt)
        deck_model = result.scalar_one_or_none()
        return deck_model.to_entity() if deck_model else None

    async def add(self, deck: Deck) -> None:
        deck_model = DeckModel.from_domain(deck)
        self.session.add(deck_model)

    async def update(self, deck: Deck) -> None:
        stmt = (
            update(DeckModel)
            .where(DeckModel.id == deck.id)
            .values(
                name=deck.name,
                description=deck.description,
            )
        )
        await self.session.execute(stmt)

    # async def delete(self, deck_id: UUID) -> None:
    #     """Удалить колоду и все её карточки (каскадное удаление).

    #     Args:
    #         deck_id: UUID колоды
    #     """
    #     ...

    # async def list_by_user(self, user_id: UUID) -> List[Deck]:
    #     """Получить список всех колод пользователя.

    #     Args:
    #         user_id: UUID пользователя

    #     Returns:
    #         Список объектов Deck
    #     """
    #     ...
