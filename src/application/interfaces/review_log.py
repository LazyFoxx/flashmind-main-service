from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ReviewLogDto:
    """
    DTO для лога ревью карточки.
    Не зависит от инфраструктуры, только данные.
    """
    id: UUID
    card_id: UUID
    deck_id: UUID
    user_id: UUID
    rating: int
    review_datetime: datetime
    next_review_datetime: datetime | None
    interval: float
    review_duration: int | None
    previous_stability: float
    previous_difficulty: float
    new_stability: float
    new_difficulty: float


class AbstractReviewLogRepository(ABC):
    @abstractmethod
    async def save(self, log: ReviewLogDto) -> None:
        """Сохранить лог ревью.

        Args:
            log: DTO лога ревью
        """
        ...

    @abstractmethod
    async def get_daily_review_counts(
        self, user_id: UUID, days: int = 30
      ) -> Dict[str, int]:
        """Получить количество повторений по дням за последние N дней.

        Args:
            user_id: UUID пользователя
            days: Количество дней (по умолчанию 30)
            
        Returns:
            Словарь {date_str: count}, где date_str в формате 'YYYY-MM-DD'
            Все дни за указанный период присутствуют, даже если count=0
         """
        ...

    @abstractmethod
    async def get_total_reviews_count(self, user_id: UUID) -> int:
         """Получить общее количество повторений карточек пользователя за все время.

        Args:
            user_id: UUID пользователя
            
        Returns:
            Общее количество повторений
         """
         ...

    @abstractmethod
    async def get_current_streak_days(self, user_id: UUID) -> int:
         """Получить текущую серию дней подряд с повторениями (streak).
         
        Args:
            user_id: UUID пользователя

        Returns:
            Текущее количество дней подряд с повторениями.
         """
         ...
