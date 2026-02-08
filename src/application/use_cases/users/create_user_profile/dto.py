from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateProfileUserInput:
    user_id: UUID
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None


@dataclass(frozen=True, slots=True)
class CreateProfileUserOutput:
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None
