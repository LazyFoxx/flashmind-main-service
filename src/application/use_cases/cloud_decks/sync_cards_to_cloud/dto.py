from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SyncCardsToCloudInput:
    deck_id: UUID
    cloud_deck_id: UUID
    is_owner: bool
    is_public: bool = False
    is_approved: bool = False


@dataclass(frozen=True, slots=True)
class SyncCardsToCloudOutput:
    added: int
    updated: int
    deleted: int

