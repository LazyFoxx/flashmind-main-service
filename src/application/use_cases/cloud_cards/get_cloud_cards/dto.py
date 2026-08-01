from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID
from src.domain.entities.cloud_card.cloud_card import CloudCardTemplate


@dataclass(frozen=True, slots=True)
class GetCloudCardsOutput:
    cards: list[CloudCardTemplate]


@dataclass(frozen=True, slots=True)
class GetCloudCardsInput:
    deck_id: UUID

