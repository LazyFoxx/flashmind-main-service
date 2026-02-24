from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities.card.card import Card


@dataclass(frozen=True, slots=True)
class GetStudyCardsInput:
    deck_id: UUID
    user_id: UUID


@dataclass(frozen=True, slots=True)
class GetStudyCardsOutput:
    total: int
    in_learning: int
    learned: int
    learning_today: int
    cards: List[Card]
