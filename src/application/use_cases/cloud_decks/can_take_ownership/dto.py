from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities import CloudDeck


@dataclass(frozen=True, slots=True)
class CanTakeOwnershipOutput:
    description_changed: bool
    cards_needed_count: int
    allowed: bool

@dataclass(frozen=True, slots=True)
class CanTakeOwnershipInput:
    user_id: UUID
    deck_id: UUID
