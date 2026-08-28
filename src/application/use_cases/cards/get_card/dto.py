from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from src.domain.entities import Card
@dataclass(frozen=True, slots=True)
class GetCardOutput:
    card: Card


@dataclass(frozen=True)
class ReviewHistoryItem:
    """Элемент истории ревью карточки."""
    review_datetime: datetime
    rating: int
    difficulty: float
    stability: float
    review_duration_ms: int


@dataclass(frozen=True)
class CardReviewStats:
    """Статистика карточки."""
    last_review_datetime: Optional[datetime]
    next_review_datetime: Optional[datetime]
    review_history: List[ReviewHistoryItem]


@dataclass(frozen=True, slots=True)
class GetCardOutput:
    card: Card
    review_stats: Optional[CardReviewStats] = None