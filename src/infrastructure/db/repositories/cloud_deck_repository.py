from typing import List, Optional
from uuid import UUID

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
