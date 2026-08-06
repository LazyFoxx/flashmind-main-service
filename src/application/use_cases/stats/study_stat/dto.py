from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class StudyStatInput:
    user_id: UUID
    days: int
    deck_id: Optional[UUID] = None


@dataclass(frozen=True, slots=True)
class StudyStatOutput:
    """
    Сырые данные для формирования финального ответа.
    """

    # one_time_metrics
    total_study_seconds: int
    total_reviews: int
    daily_review_by_rating: Dict[str, Dict[int, int]]    # {date_str: {rating: count}}

    # forecast — данные для графика
    forecast: Dict[str, int]    # {date_str: count}
    
    # review_time — данные для графика времени
    daily_review_time: Dict[str, int]    # {date_str: total_seconds}

    # hourly_breakdown — данные для графика продуктивности по часам
    hourly_breakdown: Dict[str, float]    # {hour_range: percentage}

    # difficulty_distribution — данные
    difficulty: Dict[str, int]    # {range_label: count}

    # stability_distribution — данные
    stability: Dict[str, int]    # {range_label: count}

    # card_types — данные
    card_types: Dict[str, int]    # {card_type: count}
