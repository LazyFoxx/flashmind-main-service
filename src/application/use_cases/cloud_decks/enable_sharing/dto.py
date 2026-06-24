from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from enum import Enum


class SharingType(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


@dataclass(frozen=True, slots=True)
class EnableSharingInput:
    user_id: UUID
    deck_id: UUID
    type: SharingType


@dataclass(frozen=True, slots=True)
class EnableSharingOutput:
    cloud_uuid: str
    type: SharingType  # Тоже лучше использовать Enum
    is_approved: bool
    added: int
    updated: int
    deleted: int
