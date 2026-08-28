from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities.card.card import Card


@dataclass(frozen=True, slots=True)
class ReviewDueCardInput:
    user_id: UUID
    card_id: UUID
    rating: int
    review_duration: int

@dataclass(frozen=True, slots=True)
class ReviewDueCardOutput:
    card: Card
    success: bool
