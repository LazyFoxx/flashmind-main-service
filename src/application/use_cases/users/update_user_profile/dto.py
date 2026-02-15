from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import UploadFile


@dataclass(frozen=True, slots=True)
class UpdateProfileUserInput:
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_file: Optional[UploadFile] = None
    bio: Optional[str] = None


@dataclass(frozen=True, slots=True)
class UpdateProfileUserOutput:
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None
