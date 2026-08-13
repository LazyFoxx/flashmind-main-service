from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.domain.entities.deck.deck import Deck


@dataclass(frozen=True, slots=True)
class CreateDeckInput:
    user_id: UUID
    name: str
    description: str
    color: str


@dataclass(frozen=True, slots=True)
class CreateDeckOutput:
    deck: Deck
