from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID
from src.domain.entities import Card

@dataclass(frozen=True, slots=True)
class GetCardsOutput:
    cards: list[Card]


@dataclass(frozen=True, slots=True)
class GetCardsInput:
    user_id: UUID
    deck_id: Optional[UUID]
