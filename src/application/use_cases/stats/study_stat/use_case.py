# import structlog
# from typing import Dict

# from src.application.exceptions import UserNotFoundError
# from src.application.interfaces import (
#     AbstractCloudStorage,
#     AbstractUnitOfWork,
# )

# from datetime import datetime

# from .dto import StudyStatInput, StudyStatOutput
# from src.application.interfaces.user_stats import UserStatsDto

# class StudyStatUseCase:
#     """
#     Use Case: DailyReviewStatUseCase

#     Назначение:
#         Получение статистики повторений карточек пользователем за определенный период
#         (по умолчанию — текущий месяц) с разбивкой по дням.

#         Возвращает:
#              - daily_review_counts: словарь {date: count} с количеством повторений по дням
#              - total_reviews: общее количество повторений за всё время
#              - review_series: текущая серия дней подряд (streak)
#       """

#     def __init__(self, uow: AbstractUnitOfWork, storage: AbstractCloudStorage):
#         self.uow = uow
#         self.logger = structlog.get_logger(__name__)
#         self.storage = storage


#     async def execute(self, input_dto: DailyReviewStatInput) -> DailyReviewStatOutput:

#         async with self.uow:
#              # Проверяем существование пользователя
#             user = await self.uow.users.get_by_id(input_dto.user_id)
#             if user is None:
#                 self.logger.warning(
#                     "Пользователь не найден",
#                     user_id=input_dto.user_id,
#                 )
#                 raise UserNotFoundError(user_id=str(input_dto.user_id))
              
            
#              # Получаем статистику повторений
#             stats: Dict[str, int] = await self.uow.review_logs.get_daily_review_counts(
#                 user_id=input_dto.user_id,
#                 days=input_dto.days,
#               )

#               # Получаем текущую серию дней подряд (streak)
#             review_series = await self.uow.review_logs.get_current_streak_days(
#                 user_id=input_dto.user_id
#               )
            
#             # получаем статистику пользователя (создаем если нет)
#             user_stats = await self.uow.user_stats.get_by_user_id(user_id=input_dto.user_id)
#             if not user_stats:
#               total_reviews = await self.uow.review_logs.get_total_reviews_count(
#                 user_id=input_dto.user_id
#               )
              
#               user_stats = UserStatsDto(
#                 user_id=input_dto.user_id,
#                 max_days_streak=review_series,
#                 current_days_streak=review_series,
#                 total_reviews=total_reviews
#                 )

#               await self.uow.user_stats.add(user_stats)
#               print(f"DEBUG: user_stats добавлен: {user_stats}")

#              # Проверяем, нужно ли обновить max_days_streak
#             if user_stats.max_days_streak < review_series:
#                 user_stats.max_days_streak = review_series
#                 await self.uow.user_stats.update(stats=user_stats)

#             await self.uow.commit()


#         return DailyReviewStatOutput(
#             total_reviews=user_stats.total_reviews,
#             review_series=review_series,
#             daily_review_counts=stats,
#             max_review_series=user_stats.max_days_streak,
#             )

