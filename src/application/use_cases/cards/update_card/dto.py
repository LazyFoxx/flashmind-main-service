from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateCardInput:
    user_id: UUID
    card_id: UUID
    front: str
    back: str


@dataclass(frozen=True, slots=True)
class UpdateCardOutput:
    card_id: str
    deck_id: str
    front: str
    back: str
