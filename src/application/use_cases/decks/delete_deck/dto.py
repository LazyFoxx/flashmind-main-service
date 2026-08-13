from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DeleteDeckInput:
    user_id: UUID
    deck_id: UUID
