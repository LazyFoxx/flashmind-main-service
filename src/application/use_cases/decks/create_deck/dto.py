from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateDeckInput:
    user_id: UUID
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class CreateDeckOutput:
    deck_id: str
    name: str
    description: str
    desired_retention: float
    maximum_interval: int
    color: str
    total_cards: int
    due_cards_count: int
