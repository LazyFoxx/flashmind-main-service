from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities import Deck


@dataclass(frozen=True, slots=True)
class GetUserDecksOutput:
    decks: List[Deck]


@dataclass(frozen=True, slots=True)
class GetUserDecksInput:
    user_id: UUID
    timezone: str