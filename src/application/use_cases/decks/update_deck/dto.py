from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateDeckInput:
    user_id: UUID
    deck_id: UUID
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class UpdateDeckOutput:
    deck_id: str
    name: str
    description: str
