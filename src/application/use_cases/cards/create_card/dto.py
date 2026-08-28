from dataclasses import dataclass
from typing import Optional, Any
from uuid import UUID
from src.domain.entities import Card

@dataclass(frozen=True, slots=True)
class CreateCardInput:
    user_id: UUID
    deck_id: UUID
    title: str
    front: Any
    back: Any
    hint1: Optional[str] = None
    hint2: Optional[str] = None


@dataclass(frozen=True, slots=True)
class CreateCardOutput:
    card: Card
