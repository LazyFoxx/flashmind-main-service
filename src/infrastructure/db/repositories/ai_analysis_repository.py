from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.ai_analysis import AiAnalysisModel
from src.application.interfaces import AbstractAiAnalysisRepository, AiAnalysisDto


class SQLAlchemyAiAnalysisRepository(AbstractAiAnalysisRepository):
    """Репозиторий для хранения AI-анализов статистики обучения."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, dto: AiAnalysisDto) -> UUID:
        """Upsert: создать новый или обновить существующий."""
        existing = await self._find_by_owner_and_date(
            user_id=dto.user_id,
            deck_id=dto.deck_id,
        )

        if existing:
            await self._update(existing.id, dto)
            return existing.id
        else:
            return await self._save(dto)

    async def get_latest_by_user(self, user_id: UUID) -> Optional[AiAnalysisDto]:
        """Получить самый свежий анализ по пользователю."""
        stmt = (
            select(AiAnalysisModel)
             .where(
                AiAnalysisModel.user_id == user_id,
                AiAnalysisModel.deck_id == None,
            )
             .order_by(AiAnalysisModel.analysis_date.desc())
             .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return model.to_dto()

    async def get_latest_by_deck(self, deck_id: UUID) -> Optional[AiAnalysisDto]:
        """Получить самый свежий анализ по колоде."""
        stmt = (
            select(AiAnalysisModel)
             .where(
                AiAnalysisModel.deck_id == deck_id,
                AiAnalysisModel.user_id == None,
            )
             .order_by(AiAnalysisModel.analysis_date.desc())
             .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return model.to_dto()

    async def _find_by_owner_and_date(
        self,
        user_id: Optional[UUID],
        deck_id: Optional[UUID],
    ) -> Optional[AiAnalysisDto]:
        """Внутренний метод: найти анализ по владельцу и дате."""
        conditions = []

        if user_id is not None:
            conditions.append(AiAnalysisModel.user_id == user_id)
            conditions.append(AiAnalysisModel.deck_id == None)
        elif deck_id is not None:
            conditions.append(AiAnalysisModel.deck_id == deck_id)
            conditions.append(AiAnalysisModel.user_id == None)

        stmt = select(AiAnalysisModel).where(*conditions)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return model.to_dto()

    async def _save(self, dto: AiAnalysisDto) -> UUID:
        """Внутренний метод: создать новую запись."""
        model = AiAnalysisModel.from_dto(dto)
        self.session.add(model)
        await self.session.flush()
        return model.id

    async def _update(self, model_id: UUID, dto: AiAnalysisDto) -> bool:
        """Внутренний метод: обновить существующую запись."""
        stmt = (
            update(AiAnalysisModel)
             .where(AiAnalysisModel.id == model_id)
             .values(
                stats_json=dto.stats_json,
                analysis_text=dto.analysis_text,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
