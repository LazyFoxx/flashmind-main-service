from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DeleteCardInput:
    user_id: UUID
    card_id: UUID
