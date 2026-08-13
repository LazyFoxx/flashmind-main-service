from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateCardInput:
    user_id: UUID
    deck_id: UUID
    front: str
    back: str


@dataclass(frozen=True, slots=True)
class CreateCardOutput:
    card_id: str
    deck_id: str
    front: str
    back: str
