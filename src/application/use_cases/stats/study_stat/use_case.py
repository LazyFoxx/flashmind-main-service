import structlog
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.application.exceptions import UserNotFoundError
from src.application.interfaces import (
    AbstractCloudStorage,
    AbstractUnitOfWork,
)

from .dto import StudyStatInput, StudyStatOutput


class StudyStatUseCase:
    """
    Use Case: StudyStatUseCase
    
    Назначение:
        Получение полной статистики пользователя:
         - Общее время изучения
         - Прогноз повторений на 30 дней
         - Графики повторений (ответы по дням)
         - Графики времени (секунды по дням)
         - Продуктивность по часам суток
         - Распределение по сложности
         - Распределение по стабильности
         - Типы карт (новые, изучаемые, изученные, отложенные)
    """

    def __init__(self, uow: AbstractUnitOfWork, storage: AbstractCloudStorage):
        self.uow = uow
        self.logger = structlog.get_logger(__name__)
        self.storage = storage

    async def execute(self, input_dto: StudyStatInput) -> StudyStatOutput:
        async with self.uow:
            # 1. Проверить существование пользователя
            user = await self.uow.users.get_by_id(input_dto.user_id)
            if user is None:
                self.logger.warning(
                    "Пользователь не найден",
                    user_id=input_dto.user_id,
                )
                raise UserNotFoundError(user_id=str(input_dto.user_id))

            # 2. Запрос: Общее время изучения ЗА ВСЁ ВРЕМЯ (опционально по колоде)
            total_study_seconds = await self.uow.review_logs.get_total_study_seconds(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
            )
            # общее количество повторов карточек ( опционально по колоде )
            total_reviews = await self.uow.review_logs.get_total_reviews_count(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
            )
            
            # 3. Запрос: Повторения по дням с разбивкой по рейтингам
            daily_review_by_rating = await self.uow.review_logs.get_daily_review_by_rating(
                user_id=input_dto.user_id,
                days=input_dto.days,
                deck_id=input_dto.deck_id,
            )
            
            # 4. Запрос: Суммарное время ревью в секундах по дням
            daily_review_time = await self.uow.review_logs.get_daily_review_time(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
                days=input_dto.days,
            )
            
            # 5. Запрос: Продуктивность по часам суток
            hourly_breakdown = await self.uow.review_logs.get_hourly_breakdown(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
                days=input_dto.days,
            )
            
            # 6. Запрос: Распределение по сложности
            difficulty_distribution = await self.uow.cards.get_difficulty_distribution(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
            )
            
            # 7. Запрос: Распределение по стабильности
            stability_distribution = await self.uow.cards.get_stability_distribution(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
            )
            
            # 8. Запрос: Распределение по типам карточек
            card_types_distribution = await self.uow.cards.get_card_types_distribution(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
            )
            
            # 9. Прогноз карточек на повтор
            forecast_points = await self.uow.cards.get_forecast_due_cards(
                user_id=input_dto.user_id,
                deck_id=input_dto.deck_id,
                days=180)

            return StudyStatOutput(
                total_study_seconds=total_study_seconds,
                total_reviews=total_reviews,
                daily_review_by_rating=daily_review_by_rating,
                forecast=forecast_points,
                daily_review_time=daily_review_time,
                hourly_breakdown=hourly_breakdown,
                difficulty=difficulty_distribution,
                stability=stability_distribution,
                card_types=card_types_distribution,
            )
