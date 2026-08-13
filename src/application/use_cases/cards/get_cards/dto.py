from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetCardsOutput:
    total: int
    cards: list[tuple[UUID, UUID, str, Optional[float], Optional[float]]]


@dataclass(frozen=True, slots=True)
class GetCardsInput:
    user_id: UUID
    deck_id: Optional[UUID]
    page: Optional[int]
    per_page: Optional[int]
    sort_by: Optional[str] = None       # Например: 'created_at', 'difficulty', 'stability'
    sort_order: Optional[str] = None 
