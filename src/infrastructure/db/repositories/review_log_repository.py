from datetime import datetime, timedelta, timezone
from typing import Dict, List
from uuid import UUID

from sqlalchemy import select, func, extract
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
