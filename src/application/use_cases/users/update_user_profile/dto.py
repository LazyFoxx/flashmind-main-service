from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UpdateProfileUserInput:
    user_id: UUID
    first_name: str
    last_name: str
    avatar_file: Optional[str] = None
    bio: Optional[str] = None


@dataclass(frozen=True, slots=True)
class UpdateProfileUserOutput:
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None
