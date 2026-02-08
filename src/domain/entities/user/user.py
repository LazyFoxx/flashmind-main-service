from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(slots=True, frozen=True)
class User:
    """
    Доменная сущность пользователя.
    """

    id: UUID
    first_name: str
    last_name: str
    avatar_url: str
    bio: Optional[str] = None
