from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.domain.entities.deck.deck import Deck


@dataclass(frozen=True, slots=True)
class UpdateDeckInput:
    user_id: UUID
    deck_id: UUID
    name: str
    description: str
    desired_retention: float
    maximum_interval: int
    color: str


@dataclass(frozen=True, slots=True)
class UpdateDeckOutput:
    deck: Deck
