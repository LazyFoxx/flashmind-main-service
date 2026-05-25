from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set
from uuid import UUID

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.application.interfaces import AbstractReviewLogRepository, ReviewLogDto
from src.infrastructure.db.models import ReviewLogModel


class SQLAlchemyReviewLogRepository(AbstractReviewLogRepository):
    """Репозиторий для работы с логами ревью."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, log: ReviewLogDto) -> None:
        """Сохранить лог ревью, преобразовав DTO в модель."""
        model = ReviewLogModel(
            id=log.id,
            card_id=log.card_id,
            deck_id=log.deck_id,
            user_id=log.user_id,
            rating=log.rating,
            review_datetime=log.review_datetime,
            next_review_datetime=log.next_review_datetime,
            interval=log.interval,
            review_duration=log.review_duration,
            previous_stability=log.previous_stability,
            previous_difficulty=log.previous_difficulty,
            new_stability=log.new_stability,
            new_difficulty=log.new_difficulty,
        )
        self.session.add(model)

    async def get_daily_review_counts(
        self, user_id: UUID, days: int = 28
    ) -> Dict[str, int]:
        """Получить количество повторений по дням за последние N дней."""
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)

        stmt = (
            select(
                func.date(ReviewLogModel.review_datetime).label("review_date"),
                func.count(ReviewLogModel.id).label("count"),
            )
            .where(
                ReviewLogModel.user_id == user_id,
                ReviewLogModel.review_datetime >= start_date,
            )
            .group_by(func.date(ReviewLogModel.review_datetime))
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # Создаем словарь со всеми днями и нулями
        daily_counts = {
            (now - timedelta(days=i)).strftime("%Y-%m-%d"): 0
            for i in range(days)
        }

        # Заполняем реальными данными
        for row in rows:
            date_str = row.review_date.strftime("%Y-%m-%d")
            if date_str in daily_counts:
                daily_counts[date_str] = row.count

        return daily_counts

    async def get_total_reviews_count(self, user_id: UUID) -> int:
        """Получить общее количество повторений карточек пользователя за все время."""
        stmt = (
            select(func.count(ReviewLogModel.id))
              .where(ReviewLogModel.user_id == user_id)
          )
        
        result = await self.session.execute(stmt)
        total = result.scalar_one()
        
        return total or 0

    async def get_current_streak_days(self, user_id: UUID) -> int:
        """Получить текущую серию дней подряд с повторениями (streak).

        Returns:
            Текущее количество дней подряд с повторениями.
         """
        now = datetime.now(timezone.utc)
        today = now.date()   # <-- Исправлено: получаем date, а не datetime

        # Получаем все уникальные даты с повторениями за последние 365 дней
        one_year_ago = today - timedelta(days=365)

        stmt = (
            select(func.date(ReviewLogModel.review_datetime).distinct())
               .where(
                ReviewLogModel.user_id == user_id,
                    func.date(ReviewLogModel.review_datetime) >= one_year_ago,
               )
               .order_by(func.date(ReviewLogModel.review_datetime).desc())
           )

        result = await self.session.execute(stmt)
        dates = [row[0] for row in result.all()]
        streak = 0
        
        if not dates:
            return streak

        # Проверяем, есть ли сегодня повторение
        if dates[0] == today:
             # Сегодня есть повтор — начинаем считать от сегодня
            expected_date = today

            for date in dates:
                if date == expected_date:
                    streak += 1
                    expected_date -= timedelta(days=1)
                else:
                    break

            return streak

        # Сегодня нет повтора — проверяем вчера
        yesterday = today - timedelta(days=1)
        if dates[0] == yesterday:
             # Вчера был повтор — начинаем считать от вчера
            expected_date = yesterday

            for date in dates:
                if date == expected_date:
                    streak += 1
                    expected_date -= timedelta(days=1)
                else:
                    break

            return streak

        # Ни сегодня, ни вчера — streak = 0
        return 0

