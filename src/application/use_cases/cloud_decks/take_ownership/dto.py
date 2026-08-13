from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.domain.entities import CloudDeck


@dataclass(frozen=True, slots=True)
class TakeOwnershipOutput:
    old_cloud_uuid: Optional[UUID]
    
    cloud_uuid: str
    type: str
    is_approved: bool
    added: int
    updated: int
    deleted: int

@dataclass(frozen=True, slots=True)
class TakeOwnershipInput:
    user_id: UUID
    deck_id: UUID
