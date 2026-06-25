from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import AbstractCloudDeckRepository, CloudDeck
from src.infrastructure.db.models import CloudDeckModel


class SQlAlchemyCloudDeckRepository(AbstractCloudDeckRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, deck_id: UUID,
    ) -> Optional[CloudDeck]:
        stmt = select(CloudDeckModel).where(CloudDeckModel.id == deck_id)

        result = await self.session.execute(stmt)
        deck_model = result.scalar_one_or_none()
        return deck_model.to_entity() if deck_model else None
    
    async def get_public_decks(
        self, is_approved: bool = True,
    ) -> Optional[List[CloudDeck]]:
        stmt = select(CloudDeckModel).where(
            CloudDeckModel.type == "PUBLIC",
            CloudDeckModel.is_approved == is_approved
        )

        result = await self.session.execute(stmt)
        deck_models = result.scalars().all()
        
        return [deck_model.to_entity() for deck_model in deck_models]


    async def add(self, deck: CloudDeck) -> None:
        deck_model = CloudDeckModel.from_domain(deck)
        self.session.add(deck_model)


    async def autoincr_downloaded(self, deck_id: UUID) -> None:
        """Добавляет скачивание к downloaded."""

        
        stmt = (
        update(CloudDeckModel)
            .where(CloudDeckModel.id == deck_id)
            .values(
                total_reviews=func.coalesce(CloudDeckModel.downloaded, 0) + 1,
            )
        )
        await self.session.execute(stmt)
        
        return None

    async def update_last_synced_at(self, cloud_deck_id: UUID) -> None:
        stmt = (
            update(CloudDeckModel)
            .where(CloudDeckModel.id == cloud_deck_id)
            .values(last_synced_at=func.now())
        )
        await self.session.execute(stmt)
        
    async def get_last_synced_at(self, cloud_deck_id: UUID) -> Optional[datetime]:
        stmt = select(CloudDeckModel.last_synced_at).where(CloudDeckModel.id == cloud_deck_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

