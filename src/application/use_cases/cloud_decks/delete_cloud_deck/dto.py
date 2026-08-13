from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities import CloudDeck


@dataclass(frozen=True, slots=True)
class DeleteCloudDeckOutput:
    result: bool

@dataclass(frozen=True, slots=True)
class DeleteCloudDeckInput:
    cloud_deck_id: UUID
    user_id: UUID