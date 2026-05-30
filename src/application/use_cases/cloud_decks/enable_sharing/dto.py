from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class EnableSharingInput:
    user_id: UUID
    deck_id: UUID
    type: str # "PUBLIC" или "PRIVATE"


@dataclass(frozen=True, slots=True)
class EnableSharingOutput:
    cloud_uuid: str
    type: str  
    is_approved: bool
    added: int
    updated: int
    deleted: int

