from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractDeckRepository, Deck
from src.infrastructure.db.models import CardModel, DeckModel


class SQlAlchemyDeckRepository(AbstractDeckRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, deck_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Deck]:
        stmt = select(DeckModel).where(DeckModel.id == deck_id)

        if user_id is not None:
            stmt = stmt.where(DeckModel.user_id == user_id)

        result = await self.session.execute(stmt)
        deck_model = result.scalar_one_or_none()
        return deck_model.to_entity() if deck_model else None
    
    async def get_by_cloud_deck_id(
        self, cloud_deck_id: UUID,  user_id: UUID,
    ) -> Optional[Deck]:
        stmt = select(DeckModel).where(DeckModel.cloud_deck_id == cloud_deck_id, DeckModel.user_id == user_id)
        result = await self.session.execute(stmt)
        deck_model = result.scalar_one_or_none()
        return deck_model.to_entity() if deck_model else None


    async def get_by_name(
        self, name: str, user_id: Optional[UUID] = None
    ) -> Optional[Deck]:
        stmt = select(DeckModel).where(DeckModel.name == name)

        if user_id is not None:
            stmt = stmt.where(DeckModel.user_id == user_id)

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
            .where(DeckModel.user_id == deck.user_id)
            .values(
                name=deck.name,
                description=deck.description,
                desired_retention=deck.desired_retention,
                maximum_interval=deck.maximum_interval,
                color=deck.color,
                is_cloud_deck=deck.is_cloud_deck,
                cloud_type=deck.cloud_type,
                is_approved=deck.is_approved,
                author_id=deck.author_id,
                cloud_deck_id=deck.cloud_deck_id,
            )
        )
        await self.session.execute(stmt)

    async def delete(self, deck_id: UUID, user_id: UUID) -> None:
        await self.session.execute(
            delete(DeckModel)
            .where(DeckModel.id == deck_id)
            .where(DeckModel.user_id == user_id)
        )

    async def list_by_user(self, user_id: UUID) -> List[Deck]:
        stmt = select(DeckModel).where(DeckModel.user_id == user_id)
        result = await self.session.execute(stmt)
        # Получаем все найденные модели колод, преобразуем их в сущности Deck
        deck_models = [deck_model.to_entity() for deck_model in result.scalars()]
        return deck_models

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
        stmt = (
            select(func.count())
            .select_from(CardModel)
            .where(CardModel.deck_id == deck_id)
        )
        result = await self.session.execute(stmt)

        total_cards = result.scalar_one()

        stmt = (
            select(func.count())
            .select_from(CardModel)
            .where(CardModel.deck_id == deck_id)
            .where(CardModel.in_learning)
        )
        result = await self.session.execute(stmt)

        in_learning = result.scalar_one()

        stmt = (
            select(func.count())
            .select_from(CardModel)
            .where(CardModel.deck_id == deck_id)
            .where(CardModel.stability >= 100)
        )
        result = await self.session.execute(stmt)

        learned = result.scalar_one()

        return {
            "total_cards": total_cards,
            "in_learning": in_learning,
            "learned": learned,
        }
    

