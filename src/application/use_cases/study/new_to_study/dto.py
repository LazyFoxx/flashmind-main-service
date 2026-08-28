from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities.card.card import Card


@dataclass(frozen=True, slots=True)
class NewToStudyInput:
    deck_id: UUID
    user_id: UUID
    total: int


@dataclass(frozen=True, slots=True)
class NewToStudyOutput:
    cards: List[Card]
