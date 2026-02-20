from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetCardsOutput:
    total: int
    cards: list[tuple[UUID, UUID, str]]


@dataclass(frozen=True, slots=True)
class GetCardsInput:
    user_id: UUID
    deck_id: Optional[UUID]
    page: Optional[int]
    per_page: Optional[int]
