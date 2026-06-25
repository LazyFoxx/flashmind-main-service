from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetCloudCardOutput:
    card_id: str
    front: str
    back: str
