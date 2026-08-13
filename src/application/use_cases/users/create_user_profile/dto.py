from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateUserProfileInput:
    user_id: UUID
    name: Optional[str]
    avatar_url: Optional[str]
