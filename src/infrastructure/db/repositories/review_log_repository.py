from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Dict, List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy import select, func, case, extract
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
        self, user_id: UUID, days: int = 28, timezone: str = "UTC",
    ) -> Dict[str, int]:
        """Получить количество повторений по дням за последние N дней."""

        user_tz = ZoneInfo(timezone) if timezone else ZoneInfo("UTC")
        now = datetime.now(user_tz)
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

    # async def get_total_reviews_count(self, user_id: UUID) -> int:
    #     """Получить общее количество повторений карточек пользователя за все время."""
    #     stmt = (
    #         select(func.count(ReviewLogModel.id))
    #           .where(ReviewLogModel.user_id == user_id)
    #       )
        
    #     result = await self.session.execute(stmt)
    #     total = result.scalar_one()
        
    #     return total or 0
    
    async def get_total_reviews_count(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None
    ) -> int:
        """Получить общее количество повторений карточек пользователя за все время.

        Args:
            user_id: UUID пользователя
            deck_id: Опционально — ID колоды (если None, то по всем колодам)
        """
        conditions = [ReviewLogModel.user_id == user_id]
        
        if deck_id is not None:
            conditions.append(ReviewLogModel.deck_id == deck_id)

        stmt = (
            select(func.count(ReviewLogModel.id))
                .where(*conditions)
        )
        
        result = await self.session.execute(stmt)
        total = result.scalar_one()
        
        return total or 0


    async def get_current_streak_days(self, user_id: UUID, timezone: str = "UTC") -> int:

        user_tz = ZoneInfo(timezone) if timezone else ZoneInfo("UTC")
        now = datetime.now(user_tz)
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

    async def get_total_study_seconds(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None
    ) -> int:
        """Получить общее время изучения в секундах за ВСЁ ВРЕМЯ.
        
        Args:
            user_id: UUID пользователя
            deck_id: Опционально — ID колоды (если None, то по всем колодам)
        """
        conditions = [ReviewLogModel.user_id == user_id]
        
        if deck_id is not None:
            conditions.append(ReviewLogModel.deck_id == deck_id)
        
        stmt = (
            select(func.coalesce(func.sum(ReviewLogModel.review_duration), 0))
                 .where(*conditions)
         )
        
        result = await self.session.execute(stmt)
        total_ms = result.scalar_one() or 0
        
        return total_ms // 1000    # миллисекунды → секунды

    async def get_daily_review_by_rating(
        self, 
        user_id: UUID, 
        days: int = 30,
        deck_id: Optional[UUID] = None,
        timezone: str = "UTC"  # ← Уже есть
    ) -> Dict[str, Dict[int, int]]:
        """Получить количество повторений по дням с разбивкой по рейтингам за последние N дней.

        Returns:
            Словарь {date_str: {rating: count}}, где:
            - date_str в формате 'YYYY-MM-DD'
            - rating: 1 (Again/forgotten), 2 (Hard/hard), 3 (Good/good), 4 (Easy/easy)
        """
        user_tz = ZoneInfo(timezone) if timezone else ZoneInfo("UTC")
        now = datetime.now(user_tz)
        start_date = now - timedelta(days=days)
        
        conditions = [
            ReviewLogModel.user_id == user_id,
            ReviewLogModel.review_datetime >= start_date,
         ]
        
        if deck_id is not None:
            conditions.append(ReviewLogModel.deck_id == deck_id)

        stmt = (
            select(
                func.date(ReviewLogModel.review_datetime).label("review_date"),
                ReviewLogModel.rating,
                func.count(ReviewLogModel.id).label("count"),
              )
              .where(*conditions)
              .group_by(
                func.date(ReviewLogModel.review_datetime),
                ReviewLogModel.rating,
              )
          )

        result = await self.session.execute(stmt)
        rows = result.all()

        # Создаем словарь со всеми днями и нулями
        daily_by_rating: Dict[str, Dict[int, int]] = {}
        for i in range(days):
            date_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_by_rating[date_str] = {1: 0, 2: 0, 3: 0, 4: 0}

        # Заполняем реальными данными
        for row in rows:
            date_str = row.review_date.strftime("%Y-%m-%d")
            rating = row.rating
            count = row.count
            if date_str in daily_by_rating:
                daily_by_rating[date_str][rating] = count

        return daily_by_rating


    async def get_daily_review_time(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None,
        days: int = 30,
        timezone: str = "UTC"
    ) -> Dict[str, int]:

        user_tz = ZoneInfo(timezone) if timezone else ZoneInfo("UTC")
        now = datetime.now(user_tz)
        start_date = now - timedelta(days=days)
        conditions = [
            ReviewLogModel.user_id == user_id,
            ReviewLogModel.review_datetime >= start_date,
        ]
        
        if deck_id is not None:
            conditions.append(ReviewLogModel.deck_id == deck_id)

        stmt = (
            select(
                func.date(ReviewLogModel.review_datetime).label("review_date"),
                func.sum(ReviewLogModel.review_duration).label("total_duration"),
            )
            .where(*conditions)
            .group_by(func.date(ReviewLogModel.review_datetime))
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # Создаем словарь со всеми днями и нулями
        daily_time: Dict[str, int] = {}
        for i in range(days):
            date_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_time[date_str] = 0

        # Заполняем реальными данными (миллисекунды → секунды)
        for row in rows:
            date_str = row.review_date.strftime("%Y-%m-%d")
            total_ms = row.total_duration or 0
            if date_str in daily_time:
                daily_time[date_str] = total_ms // 1000

        return daily_time


    async def get_hourly_breakdown(
        self,
        user_id: UUID,
        deck_id: Optional[UUID] = None,
        days: int = 30,
        timezone: str = "UTC",
    ) -> Dict[str, float]:
        """Получить продуктивность по часам суток за последние N дней.

        Returns:
            Словарь {hour_range: percentage}, где:
                 - hour_range: '00:00-04:00', '04:00-08:00', ..., '20:00-24:00'
                 - percentage: процент правильно отвеченных (Good + Easy) от всех ответов
        """

        user_tz = ZoneInfo(timezone) if timezone else ZoneInfo("UTC")
        now = datetime.now(user_tz)
        start_date = now - timedelta(days=days)
        
        # Подзапрос: вычисляем hour_index для каждой записи
        base_conditions = [
            ReviewLogModel.user_id == user_id,
            ReviewLogModel.review_datetime >= start_date,
        ]
        
        if deck_id is not None:
            base_conditions.append(ReviewLogModel.deck_id == deck_id)

        # Создаем подзапрос для вычисления hour_index
        hourly_subquery = (
            select(
                ReviewLogModel.id.label('log_id'),
                ReviewLogModel.rating.label('log_rating'),
                case(
                    (extract('hour', ReviewLogModel.review_datetime) < 4, 0),
                    (extract('hour', ReviewLogModel.review_datetime) < 8, 1),
                    (extract('hour', ReviewLogModel.review_datetime) < 12, 2),
                    (extract('hour', ReviewLogModel.review_datetime) < 16, 3),
                    (extract('hour', ReviewLogModel.review_datetime) < 20, 4),
                    else_=5,
                ).label('hour_index'),
            )
            .where(*base_conditions)
            .subquery()
        )

        # Основной запрос: агрегация по hour_index из подзапроса
        stmt = (
            select(
                case(
                    (hourly_subquery.c.hour_index == 0, '00:00-04:00'),
                    (hourly_subquery.c.hour_index == 1, '04:00-08:00'),
                    (hourly_subquery.c.hour_index == 2, '08:00-12:00'),
                    (hourly_subquery.c.hour_index == 3, '12:00-16:00'),
                    (hourly_subquery.c.hour_index == 4, '16:00-20:00'),
                    else_='20:00-24:00',
                ).label('hour_range'),
                func.count(hourly_subquery.c.log_id).label('total_count'),
                func.sum(
                    case(
                        (hourly_subquery.c.log_rating.in_([3, 4]), 1),
                        else_=0,
                    )
                ).label('good_easy_count'),
            )
            .group_by(hourly_subquery.c.hour_index)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # Создаем словарь со всеми диапазонами и нулями
        hour_ranges = ['00:00-04:00', '04:00-08:00', '08:00-12:00',
                       '12:00-16:00', '16:00-20:00', '20:00-24:00']
        hourly_data: Dict[str, Dict[str, int]] = {
            hr: {'total_count': 0, 'good_easy_count': 0} for hr in hour_ranges
        }

        # Заполняем реальными данными
        for row in rows:
            hr = row.hour_range
            hourly_data[hr]['total_count'] = row.total_count
            hourly_data[hr]['good_easy_count'] = row.good_easy_count

        # Вычисляем проценты
        hourly_percentage: Dict[str, float] = {}
        for hr in hour_ranges:
            total = hourly_data[hr]['total_count']
            good_easy = hourly_data[hr]['good_easy_count']
            if total > 0:
                hourly_percentage[hr] = (good_easy / total) * 100
            else:
                hourly_percentage[hr] = 0.0

        return hourly_percentage
    
    async def get_card_review_history(
        self,
        card_id: UUID,
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(
                ReviewLogModel.review_datetime.label('review_datetime'),
                ReviewLogModel.rating.label('rating'),
                ReviewLogModel.new_difficulty.label('difficulty'),
                ReviewLogModel.new_stability.label('stability'),
                ReviewLogModel.review_duration.label('review_duration_ms'),
            )
            .where(ReviewLogModel.card_id == card_id)
            .order_by(ReviewLogModel.review_datetime.asc())
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                'review_datetime': row.review_datetime,
                'rating': row.rating,
                'difficulty': row.difficulty,
                'stability': row.stability,
                'review_duration_ms': row.review_duration_ms,
            }
            for row in rows
        ]
