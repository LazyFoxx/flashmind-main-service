from dataclasses import dataclass
from typing import Optional, Any
from uuid import UUID
from src.domain.entities import Card

@dataclass(frozen=True, slots=True)
class UpdateCardInput:
    user_id: UUID
    card_id: UUID
    title: Optional[str] = None
    front: Optional[Any] = None
    back: Optional[Any] = None
    hint1: Optional[str] = None
    hint2: Optional[str] = None
    is_suspended: Optional[bool] = None


@dataclass(frozen=True, slots=True)
class UpdateCardOutput:
    card: Card
