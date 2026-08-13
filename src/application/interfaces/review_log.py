from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
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
        self, user_id: UUID, days: int = 30, timezone: str = "UTC"
    ) -> Dict[str, int]:
        """Получить количество повторений по дням за последние N дней.

        Args:
            user_id: UUID пользователя
            days: Количество дней (по умолчанию 30)
            timezone: IANA таймзона (по умолчанию "UTC")
            
        Returns:
            Словарь {date_str: count}, где date_str в формате 'YYYY-MM-DD'
            Все дни за указанный период присутствуют, даже если count=0
        """
        ...


    @abstractmethod
    async def get_total_reviews_count(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None
    ) -> int:
        """Получить общее количество повторений карточек пользователя за все время.

        Args:
            user_id: UUID пользователя
            deck_id: Опционально — ID колоды (если None, то по всем колодам)
            
        Returns:
            Общее количество повторений
        """
        ...


    @abstractmethod
    async def get_current_streak_days(
        self, user_id: UUID, timezone: str = "UTC"
    ) -> int:
        """Получить текущую серию дней подряд с повторениями (streak).
        
        Args:
            user_id: UUID пользователя
            timezone: IANA таймзона (по умолчанию "UTC")

        Returns:
            Текущее количество дней подряд с повторениями.
        """
        ...

    
    @abstractmethod
    async def get_total_study_seconds(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None
    ) -> int:
        """Получить общее время изучения в секундах за ВСЁ ВРЕМЯ.
        
        Args:
            user_id: UUID пользователя
            deck_id: Опционально — ID колоды (если None, то по всем колодам)
            
        Returns:
            Общее время в секундах (сумма review_duration для всех ревью пользователя)
        """
        ...
    
    @abstractmethod
    async def get_daily_review_by_rating(
        self, 
        user_id: UUID, 
        days: int = 30,
        deck_id: Optional[UUID] = None,
        timezone: str = "UTC"  # ← ДОБАВИТЬ
    ) -> Dict[str, Dict[int, int]]:
        """Получить количество повторений по дням с разбивкой по рейтингам за последние N дней.

        Args:
            user_id: UUID пользователя
            days: Количество дней (по умолчанию 30)
            deck_id: Опционально — ID колоды
            timezone: IANA таймзона (по умолчанию "UTC")

        Returns:
            Словарь {date_str: {rating: count}}
        """
        ...
    
    @abstractmethod
    async def get_daily_review_time(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None,
        days: int = 30,
        timezone: str = "UTC"  # ← ДОБАВИТЬ
    ) -> Dict[str, int]:
        """Получить суммарное время ревью в секундах по дням за последние N дней.

        Args:
            user_id: UUID пользователя
            deck_id: Опционально — ID колоды
            days: Количество дней (по умолчанию 30)
            timezone: IANA таймзона (по умолчанию "UTC")

        Returns:
            Словарь {date_str: total_seconds}
        """
        ...
    
    @abstractmethod
    async def get_hourly_breakdown(
        self, 
        user_id: UUID, 
        deck_id: Optional[UUID] = None,
        days: int = 30,
        timezone: str = "UTC"  # ← ДОБАВИТЬ
    ) -> Dict[str, float]:
        """Получить продуктивность по часам суток за последние N дней.

        Args:
            user_id: UUID пользователя
            deck_id: Опционально — ID колоды
            days: Количество дней (по умолчанию 30)
            timezone: IANA таймзона (по умолчанию "UTC")

        Returns:
            Словарь {hour_range: percentage}
        """
        ...


