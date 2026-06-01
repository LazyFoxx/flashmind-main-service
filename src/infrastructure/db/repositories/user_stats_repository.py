from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.user_stats import UserStatsModel
from src.application.interfaces import AbstractUserStatsRepository, UserStatsDto


class SQLAlchemyUserStatsRepository(AbstractUserStatsRepository):
    """Репозиторий для статистики пользователя."""

    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserStatsDto]:
        """Получить статистику пользователя по ID."""
        stmt = select(UserStatsModel).where(UserStatsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None

        return UserStatsDto(
            user_id=model.user_id,
            max_days_streak=model.max_days_streak,
            current_days_streak=model.current_days_streak,
            update_at=model.updated_at
        )

    async def update(self, stats: UserStatsDto) -> None:
        """Обновляет статистику пользователя."""

         # Проверяем, существует ли запись
        existing = await self.get_by_user_id(stats.user_id)
        
        if existing is None:
              # Записи нет — создаем новую
            new_stats = UserStatsModel(
                user_id=stats.user_id,
                max_days_streak=stats.max_days_streak,
                current_days_streak=stats.current_days_streak,
               )
            self.session.add(new_stats)
        else:
              # Запись есть — обновляем через явный UPDATE
            stmt = (
            update(UserStatsModel)
              .where(UserStatsModel.user_id == user_id)
              .values(
                max_days_streak=stats.max_days_streak,
                current_days_streak=stats.current_days_streak,
              )
        )
        await self.session.execute(stmt)

