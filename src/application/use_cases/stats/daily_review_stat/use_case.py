import structlog
from typing import Dict

from src.application.exceptions import UserNotFoundError
from src.application.interfaces import (
    AbstractCloudStorage,
    AbstractUnitOfWork,
)

from .dto import DailyReviewStatInput, DailyReviewStatOutput


class DailyReviewStatUseCase:
    """
    Use Case: DailyReviewStatUseCase

    Назначение:
        Получение статистики повторений карточек пользователем за определенный период
        (по умолчанию — текущий месяц) с разбивкой по дням.

        Возвращает:
             - daily_review_counts: словарь {date: count} с количеством повторений по дням
             - total_reviews: общее количество повторений за всё время
             - review_series: текущая серия дней подряд (streak)
      """

    def __init__(self, uow: AbstractUnitOfWork, storage: AbstractCloudStorage):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.storage = storage

    async def execute(self, input_dto: DailyReviewStatInput) -> DailyReviewStatOutput:

        async with self.uow:
             # Проверяем существование пользователя
            user = await self.uow.users.get_by_id(input_dto.user_id)
            if user is None:
                self.logger.warning(
                    "Пользователь не найден",
                    user_id=input_dto.user_id,
                )
                raise UserNotFoundError(user_id=str(input_dto.user_id))

             # Получаем статистику повторений
            stats: Dict[str, int] = await self.uow.review_logs.get_daily_review_counts(
                user_id=input_dto.user_id,
                days=input_dto.days,
              )

              # Получаем общее количество повторений
            total_reviews = await self.uow.review_logs.get_total_reviews_count(
                user_id=input_dto.user_id
              )

              # Получаем текущую серию дней подряд (streak)
            review_series = await self.uow.review_logs.get_current_streak_days(
                user_id=input_dto.user_id
              )

            self.logger.info(
                  "Получена статистика повторений",
                user_id=str(input_dto.user_id),
                total_reviews=total_reviews,
                review_series=review_series,
                days_requested=input_dto.days,
              )

        return DailyReviewStatOutput(
            total_reviews=total_reviews,
            review_series=review_series,
            daily_review_counts=stats,
          )
