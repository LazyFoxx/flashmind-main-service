from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateDeckSettingsInput:
    user_id: UUID
    deck_id: UUID
    desired_retention: float
    maximum_interval: int
    color: str


@dataclass(frozen=True, slots=True)
class UpdateDeckSettingsOutput:
    deck_id: UUID
    desired_retention: float
    maximum_interval: int
    color: str
