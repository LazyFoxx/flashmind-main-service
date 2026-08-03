from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class StudyStatInput:
    user_id: UUID
    days: int


@dataclass(frozen=True, slots=True)
class StudyStatOutput:
    total_reviews: int
    review_series: int
    max_review_series: int
    daily_review_counts: Dict[str, int]
