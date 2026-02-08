from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetProfileUserInput:
    user_id: UUID


@dataclass(frozen=True, slots=True)
class GetProfileUserOutput:
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None
