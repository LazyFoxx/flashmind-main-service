from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetCardOutput:
    card_id: str
    deck_id: str
    front: str
    back: str
