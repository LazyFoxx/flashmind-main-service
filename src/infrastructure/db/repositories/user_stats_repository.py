from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, func
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
            update_at=model.updated_at,
            total_reviews=model.total_reviews
        )


    async def add(self, stats: UserStatsDto) -> None:
        """Добавляет новую статистику пользователя."""
         # Проверяем, существует ли уже запись
        existing = await self.get_by_user_id(stats.user_id)
        if existing:
            return   # Уже существует, ничего не делаем

         # Создаем новую запись
        new_stats = UserStatsModel(
            user_id=stats.user_id,
            max_days_streak=stats.max_days_streak,
            current_days_streak=stats.current_days_streak,
            total_reviews=stats.total_reviews,
         )
        self.session.add(new_stats)
    
    async def update(self, stats: UserStatsDto) -> None:
        """Обновляет статистику пользователя."""
        stmt = (
        update(UserStatsModel)
            .where(UserStatsModel.user_id == stats.user_id)
            .values(
            max_days_streak=stats.max_days_streak,
            current_days_streak=stats.current_days_streak,
            total_reviews=stats.total_reviews,
            )
        )
        await self.session.execute(stmt)
        
    async def autoincr_review(self, user_id: UUID) -> None:
        """Добавляет повтор к total reviews."""
         # Сначала проверяем, существует ли запись
        stmt = select(UserStatsModel).where(UserStatsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
             # Если записи нет, создаем её с total_reviews = 1
            new_stats = UserStatsModel(
                user_id=user_id,
                max_days_streak=0,
                current_days_streak=0,
                total_reviews=1,
             )
            self.session.add(new_stats)
        else:
             # Если запись есть, инкрементируем total_reviews
            stmt = (
                update(UserStatsModel)
                 .where(UserStatsModel.user_id == user_id)
                 .values(
                    total_reviews=model.total_reviews + 1,
        )
             )
        await self.session.execute(stmt)