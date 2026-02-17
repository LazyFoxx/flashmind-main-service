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
