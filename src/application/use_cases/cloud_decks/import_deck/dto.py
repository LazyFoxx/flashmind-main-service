from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ImportDeckInput:
    user_id: UUID
    cloud_uuid: UUID


@dataclass(frozen=True, slots=True)
class ImportDeckOutput:
    deck_id: UUID
    added: int