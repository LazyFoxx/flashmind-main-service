from datetime import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID


from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractCloudCardTemplateRepository, CloudCardTemplate
from src.infrastructure.db.models import CloudCardTemplateModel


class SQlAlchemyCloudCardTemplateRepository(AbstractCloudCardTemplateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, card: CloudCardTemplate) -> None:
        card_model = CloudCardTemplateModel.from_domain(card)
        self.session.add(card_model)
    
    async def get_by_id(self, card_id: UUID) -> Optional[CloudCardTemplate]:
        stmt = select(CloudCardTemplateModel).where(CloudCardTemplateModel.id == card_id)
        result = await self.session.execute(stmt)
        card_model = result.scalar_one_or_none()
        return card_model.to_entity() if card_model else None

    async def update(self, card: CloudCardTemplate) -> None:

        stmt = (
            update(CloudCardTemplateModel)
            .where(CloudCardTemplateModel.id == card.id)
            .values(
                front=card.front,
                back=card.back,

            )
        )
        await self.session.execute(stmt)

    async def delete(self, card_id: UUID) -> None:
        await self.session.execute(delete(CloudCardTemplateModel).where(CloudCardTemplateModel.id == card_id))


    async def get_by_deck_id(
        self,
        cloud_deck_id: UUID,
    ) -> List[CloudCardTemplate]:

        # Базовый запрос, выбираем все карточки в deck
        query = select(CloudCardTemplateModel).where(CloudCardTemplateModel.cloud_deck_id == cloud_deck_id)

        result = await self.session.execute(query)
        card_models = result.scalars().all()

        return [card_model.to_entity() for card_model in card_models]
        ...
    
    async def get_total_cards_count(self, cloud_deck_id: UUID) -> int:
        stmt = select(func.count(CloudCardTemplateModel.id)).where(
            CloudCardTemplateModel.cloud_deck_id == cloud_deck_id
        )
        
        result = await self.session.execute(stmt)
        count = result.scalar()
        
        return count if count else 0
