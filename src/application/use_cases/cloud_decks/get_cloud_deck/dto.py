from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities import CloudDeck


@dataclass(frozen=True, slots=True)
class GetCloudDeckOutput:
    deck: CloudDeck

@dataclass(frozen=True, slots=True)
class GetCloudDeckInput:
    deck_id: UUID